"""
MIT License

Copyright (c) 2025 Sanquez Heard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from kivy.logger import Logger
from kivy.utils import platform
import threading

if platform == 'android':
    from jnius import autoclass, JavaException
    AudioRecord = autoclass("android.media.AudioRecord")
    AudioSource = autoclass("android.media.MediaRecorder$AudioSource")
    AudioFormat = autoclass("android.media.AudioFormat")
    AudioTrack = autoclass("android.media.AudioTrack")
    AudioManager = autoclass("android.media.AudioManager")
    Socket = autoclass("java.net.Socket")
    SSLSocket = autoclass("javax.net.ssl.SSLSocketFactory")
    SocketTimer = autoclass("java.net.InetSocketAddress")
    SSLContext = autoclass("javax.net.ssl.SSLContext")
    SecureRandom = autoclass("java.security.SecureRandom")
    class Client:
        # Variables to be configured per client
        client_id = ""  # Used to identify/authenticate client's connection
        dst_address = "127.0.0.1"  # Use root domain for ssl connection
        dst_port = 8080
        timeout = 5  # Sets WAN timeout. LAN connection max is 2 secs.
        ssl = False
        tls_version = ""  # Defaults to auto selection. TLSv1.3 and TLSv1.2 are options
        debug = False
        # Variables to adjust audio format and quality. Default settings recommended for iOS compatibility
        SAMPLE_RATE = 16000
        CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        buffer_size = 640
        # Variables to be assigned dynamic values for VOIP services
        socket = None
        connected = False
        hasPermission = False
        data_output_stream = None
        data_input_stream = None
        audio_record = None
        active_call = False

        def __init__(self):
            min_buffer_size = AudioRecord.getMinBufferSize(
                self.SAMPLE_RATE, self.CHANNEL_CONFIG, self.AUDIO_FORMAT
            )
            if min_buffer_size > self.buffer_size:
                self.buffer_size = min_buffer_size

        def send_client_id(self):
            try:
                self.data_output_stream.write(self.client_id.encode())
                self.data_output_stream.flush()
                if self.debug:
                    Logger.info("VOIP: Client ID sent")
            except JavaException as e:
                if self.debug:
                    Logger.info("VOIP: Client ID delivery failed")
                    Logger.error(f"VOIP: {e}")

        def start_call(self):
            if self.debug:
                Logger.info("VOIP: Starting call")
            self.verifyPermission()
            if self.hasPermission:
                self.connected = False
                timeout = self.timeout * 1000
                if self.debug:
                    Logger.info(f"VOIP: {self.timeout} sec(s) wait for connection")
                try:
                    if self.ssl:
                        if self.tls_version == "":
                            ssl_socket_factory = SSLSocket.getDefault()
                        else:
                            ssl_context = SSLContext.getInstance(self.tls_version)
                            ssl_context.init(None, None, SecureRandom())
                            ssl_socket_factory = ssl_context.getSocketFactory()
                        self.socket = ssl_socket_factory.createSocket()
                    else:
                        self.socket = Socket()
                    self.socket.connect(
                        SocketTimer(self.dst_address, self.dst_port),
                        timeout
                    )
                    self.socket.setSoTimeout(timeout)
                    self.data_input_stream = self.socket.getInputStream()
                    self.data_output_stream = self.socket.getOutputStream()
                    self.connected = True
                    if self.debug:
                        Logger.info(f"VOIP: Connected to {self.dst_address}:{self.dst_port}")
                except JavaException as e:
                    if self.debug:
                        Logger.error(
                            "VOIP: "
                            "Ensure INTERNET and ACCESS_NETWORK_STATE permissions are in buildozer.spec "
                            "and server is available."
                        )
                        Logger.error(f"VOIP: {e}")
                if self.connected:
                    self.active_call = True
                    if self.client_id != "":
                        self.send_client_id() 
                    self.record_thread = threading.Thread(target=self.send_audio, daemon=True)
                    self.record_thread.start()
                    self.listening_thread = threading.Thread(target=self.receive_audio, daemon=True)
                    self.listening_thread.start()

        def end_call(self):
            if self.debug:
                Logger.info("VOIP: Ending call")
            self.active_call = False
            if hasattr(self, "record_thread") and self.record_thread.is_alive():
                self.record_thread.join()
            if hasattr(self, "listening_thread") and self.listening_thread.is_alive():
                self.listening_thread.join()
            if self.socket != None:
                self.socket.close()
                self.socket = None
            if self.debug:
                Logger.info("VOIP: Call ended")

        def verifyPermission(self):
            self.hasPermission = False
            self.audio_record = AudioRecord(
                AudioSource.VOICE_COMMUNICATION,
                self.SAMPLE_RATE,
                self.CHANNEL_CONFIG,
                self.AUDIO_FORMAT,
                self.buffer_size,
            )
            if self.audio_record.getState() != AudioRecord.STATE_UNINITIALIZED:
                self.hasPermission = True
                if self.debug:
                    Logger.info("VOIP: Microphone permission granted")
            else:
                if self.debug:
                    Logger.error(
                        "VOIP: Permission Error: "
                        "Ensure RECORD_AUDIO (Mic) permission is enabled in app settings"
                    )

        def send_audio(self):
            audio_data = bytearray(self.buffer_size)
            self.audio_record.startRecording()
            if self.debug:
                Logger.info("VOIP: Microphone live stream started")
            while self.active_call == True:
                try:
                    bytes_read = self.audio_record.read(
                        audio_data, 0, self.buffer_size
                    )
                    if (
                        bytes_read != AudioRecord.ERROR_INVALID_OPERATION
                        and bytes_read != AudioRecord.ERROR_BAD_VALUE
                    ):
                        self.data_output_stream.write(audio_data, 0, bytes_read)
                    elif bytes_read == AudioRecord.ERROR_INVALID_OPERATION:
                        if self.debug:
                            Logger.warning("VOIP: ERROR_INVALID_OPERATION on microphone")
                    else:
                        if self.debug:
                            Logger.warning("VOIP: ERROR_BAD_VALUE on microphone")
                except JavaException as e:
                    self.active_call = False
                    if self.debug:
                        Logger.error("VOIP: Microphone Stream Error")
                        Logger.error(f"VOIP: {e}")

            self.audio_record.stop()
            if self.debug:
                Logger.info("VOIP: Microphone live stream ended")
        
        def receive_audio(self):
            audio_track = AudioTrack(
                AudioManager.STREAM_VOICE_CALL,
                self.SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                self.AUDIO_FORMAT,
                self.buffer_size,
                AudioTrack.MODE_STREAM,
            )
            buffer = bytearray(self.buffer_size)
            audio_track.play()
            if self.debug:
                Logger.info("VOIP: Speaker live stream started")
            try:
                while self.active_call == True:
                    bytes_received = self.data_input_stream.read(buffer)
                    if bytes_received > 0:
                        audio_track.write(buffer, 0, bytes_received)
            except JavaException as e:
                self.active_call = False
                if self.debug:
                    Logger.error("VOIP: Speaker Stream Error")
                    Logger.error(f"VOIP: {e}")

            audio_track.stop()
            if self.debug:
                Logger.info("VOIP: Speaker live stream ended")

elif platform == 'ios':
    from pyobjus import autoclass
    from pyobjus.dylib_manager import load_framework
    load_framework("/System/Library/Frameworks/AVFoundation.framework")
    load_framework("/System/Library/Frameworks/Foundation.framework")
    load_framework("./Voip.framework")

    AVAudioEngine = autoclass("AVAudioEngine")
    AVAudioPlayerNode = autoclass("AVAudioPlayerNode")
    AVAudioFormat = autoclass("AVAudioFormat")
    VoipMachine = autoclass("Voip")
    AVAudioSession = autoclass("AVAudioSession")
    NSError = autoclass("NSError")

    class Client:
        # Variables to be configured per client
        client_id = ""  # Used to identify/authenticate client's connection
        dst_address = "127.0.0.1"  # Use root domain for ssl connection
        dst_port = 8080
        timeout = 5  # Sets WAN timeout. LAN connection max is 2 secs.
        ssl = False
        tls_version = ""  # Defaults to auto selection. TLSv1.3 and TLSv1.2 are options
        debug = False
        # Variables to adjust audio format and quality. Default settings recommended for Android compatibility
        format = 3
        sample_rate = 16000.0
        channels = 1
        interleaved = False
        buffersize = 640
        # Variables to be assigned dynamic values for VOIP services
        input_node = None
        hasPermission = False
        connected = False
        active_call = False
        error = None
        debug = False

        def __init__(self):
            self.audio_engine = AVAudioEngine.alloc().init()
            self.player_node = AVAudioPlayerNode.alloc().init()
            self.processor = VoipMachine.alloc().init()
            self.processor.audioPlayerNode = self.player_node
            self.processor.inputAudioFormat = (
                AVAudioFormat.alloc().initWithCommonFormat_sampleRate_channels_interleaved_(
                    1, 48000.0, 1, False
                )
            )
            self.processor.outputAudioFormat = (
                AVAudioFormat.alloc().initWithCommonFormat_sampleRate_channels_interleaved_(
                    self.format, self.sample_rate, self.channels, self.interleaved
                )
            )
            self.error = NSError.alloc().initWithDomain_code_userInfo_(
                "org.kivy.voip", -1, None
            )

        def verify_permission(self):
            self.hasPermission = False
            self.session = AVAudioSession.sharedInstance()
            record_permission_int = self.session.recordPermission

            if record_permission_int == 1735552628:
                self.hasPermission = True
                if self.debug:
                    Logger.info("VOIP: Microphone permission granted")
                return
            if record_permission_int == 1970168948:
                self.hasPermission = self.processor.requestMicrophonePermission()
                self.session = AVAudioSession.sharedInstance()
                record_permission_int = self.session.recordPermission
                if record_permission_int == 1735552628:
                    self.hasPermission = True
                    if self.debug:
                        Logger.info("VOIP: Microphone permission granted")
                    return
            if record_permission_int == 1684369017:
                record_permission = "Denied"
            elif record_permission_int == 1970168948:
                record_permission = "Undetermined"
            else:
                record_permission = "Unknown"

            if self.debug:
                Logger.error(
                    f"VOIP: Error: {record_permission} permission. "
                    "Ensure NSMicrophoneUsageDescription permission is in "
                    "Info.plist and mic access is granted in app settings."
                )

        def configure_audio_session(self):
            session = AVAudioSession.sharedInstance()
            try:
                session.setCategory_mode_options_error_(
                    "AVAudioSessionCategoryPlayAndRecord",
                    "AVAudioSessionModeVoiceChat",
                    0,
                    self.error,
                )
                session.setActive_error_(True, self.error)
                if self.debug:
                    Logger.info("VOIP: Audio session configured successfully.")
            except Exception as e:
                if self.debug:
                    Logger.error(f"VOIP: Failed to configure audio session: {e}")

        def start_call(self):
            if self.debug:
                Logger.info("VOIP: Starting call")
            self.verify_permission()
            if self.hasPermission:
                self.connected = False
                if self.debug:
                    Logger.info(f"VOIP: {self.timeout} sec(s) wait for connection")
                self.processor.connect_port_ssl_tlsVersion_timeout_(
                    self.dst_address, self.dst_port, self.ssl, self.tls_version, self.timeout
                )
                if self.processor.connected():
                    if self.debug:
                        Logger.info(f"VOIP: Connected to {self.dst_address}:{self.dst_port}")
                    self.connected = True
                    self.active_call = True
                    if self.client_id != "":
                        self.processor.sendClientID_(self.client_id)
                    self.configure_audio_session()
                    self.start_audio_engine()
                    threading.Thread(target=self.track_call_activity, daemon=True).start()
                else:
                    if self.debug:
                        Logger.error(
                            f"VOIP: Could not connect to {self.dst_address}:{self.dst_port}. "
                            "Ensure server is reachable."
                        )

        def track_call_activity(self):
            while self.processor.callActive:
                pass
            if self.debug:
                Logger.info("VOIP: Audio stream ended.")
            self.active_call = False

        def start_audio_engine(self):
            self.input_node = self.audio_engine.inputNode
            self.audio_engine.attachNode_(self.player_node)
            self.audio_engine.connect_to_format_(
                self.player_node,
                self.audio_engine.mainMixerNode,
                self.processor.inputAudioFormat,
            )
            self.audio_engine.prepare()
            try:
                self.audio_engine.startAndReturnError_(None)
                self.player_node.play()
                self.processor.receiveAudioData()
                audioFrames = int(self.buffersize / (16 / 8 * self.channels))
                self.processor.installTapOnBus_bufferSize_(self.input_node, audioFrames)
                if self.debug:
                    Logger.info("VOIP: Audio engine started successfully.")
                    Logger.info("VOIP: Streaming audio")
            except Exception as e:
                if self.debug:
                    Logger.error(f"VOIP: Failed to start audio engine: {e}")

        def end_call(self):
            if self.debug:
                Logger.info("VOIP: Ending call")
            if self.active_call:
                self.input_node.removeTapOnBus_(0)
                self.audio_engine.stop()
                self.player_node.stop()
            if self.processor.connected():
                self.processor.disconnect()
            if self.debug:
                Logger.info("VOIP: Call ended")
