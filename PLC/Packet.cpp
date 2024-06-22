// Mitsubishi Melsec Q series PLC 
// C#, converting data into a packet

// Generate the packet of SEND command for reading data in PlC

[Serializable]
    [StructLayout(LayoutKind.Sequential, Pack=1)]
    struct _3E_BIN_REQUEST_COMMAND
    {
        public ushort wSubHeader;     // 서브 머리글
        public byte byNetworkNo;      // 네트워크 번호
        public byte byPlcNo;          // PLC 번호
        public ushort wModuleIONo;    // 요구 상대 모듈 I/O 번호	
        public byte byModuleStateNo;  // 요구 상대 모듈 국번호
        public ushort wDataLength;    // 요구 데이터 길이
        public ushort wCpuTimer;      // CPU 감시 타이머
        public ushort wCommand;       // Command(Read)
        public ushort wSubCommand;    // Sub Command

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 3)]
        public byte[] byDeviceAddr; // 선두 Device Addr
        public byte byDeviceCode;   // Device 코드
        public ushort wCount;        // 읽기/쓰기 점수
    };


3E_BIN_REQUEST_COMMAND _Request_Header = new _3E_BIN_REQUEST_COMMAND();
            _Request_Header.byDeviceAddr = new byte[3];

            int dwTemp = 0x64; // 주소

	        _Request_Header.wSubHeader	= 0x0050;// 바이너리 50 Subheader			
	        _Request_Header.byNetworkNo	= 0x00;				
	        _Request_Header.byPlcNo		= 0xFF;				
	        _Request_Header.wModuleIONo	= 0x03FF;			
	        _Request_Header.byModuleStateNo	= 0x00;				
	        _Request_Header.wDataLength		= 0x000C;			
	        _Request_Header.wCpuTimer		= 0x0010;			
	        _Request_Header.wCommand			= 0x0401;// read command '0401';		
	        _Request_Header.wSubCommand		= 0x0001;			
	        _Request_Header.byDeviceAddr[0]	= (byte)(dwTemp	& 0x000000FF);
            _Request_Header.byDeviceAddr[1]  = (byte)(dwTemp >> 8 & 0x000000FF);
            _Request_Header.byDeviceAddr[2]  = (byte)(dwTemp >> 16 & 0x000000FF);
            _Request_Header.byDeviceCode     = 0xC2; // T
            _Request_Header.wCount  = (ushort)3; // 읽을 수량

            byte[] buffer = new byte[Marshal.SizeOf(_Request_Header)];

            unsafe
            {
                fixed (byte* fixed_buffer = buffer)
                {

                    Marshal.StructureToPtr(_Request_Header, (IntPtr)fixed_buffer, false);
                }
            }

