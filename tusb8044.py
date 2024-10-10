DEV_VENDOR_ID = 0x0451
DEV_PRODUCT_ID = 0x82ff

I2C_READ_OPCODE=0x1
I2C_WRITE_WITH_STOP_OPCODE=0x2
I2C_WRITE_NO_STOP_OPCODE=0x3


class TUSB8044():
    def __init__(self, dev):
        self._dev = dev

    
    def _set_report(self, opcode, addr, txlen, data=None):
        data_or_wLength = bytes([opcode, addr, txlen])
        if data is not None:
            data_or_wLength += data
        self._dev.ctrl_transfer(0x21, 0x09, 0x0200, 0x0, data_or_wLength = data_or_wLength)
    
    def _get_report(self, length):
        return self._dev.ctrl_transfer(0xA1, 0x01, 0x0100, 0x0, data_or_wLength = length)
    
    def _get_report_feature(self, length=2):
        return self._dev.ctrl_transfer(0xA1, 0x01, 0x0300, 0x0, data_or_wLength = length)
    
    def i2c_write(self, i2c_addr, data_bytes):
        size = len(data_bytes)
        if size >= 256:
            raise Exception("Cannot i2c write more than 256 bytes")

        self._set_report(I2C_WRITE_WITH_STOP_OPCODE, i2c_addr, size, data_bytes)
        return self._get_report([1])

    def i2c_read(self, i2c_addr, byte_cnt=1):
        self._set_report(I2C_READ_OPCODE, i2c_addr, byte_cnt, None)
        return self._get_report([1 + byte_cnt])
    
    
    

if __name__ == '__main__':
    import sys
    import usb
    import time

    dev = usb.core.find(idVendor = DEV_VENDOR_ID, idProduct = DEV_PRODUCT_ID)

    if dev is None:
        print("No tus8044 hce device found (idVendor = {} idProduct = {})".format(DEV_VENDOR_ID, DEV_PRODUCT_ID))
        sys.exit(1)
    
    print("Found tusb8044 on bus {} addr {}".format(dev.bus, dev.address))
    try:
        dev.detach_kernel_driver(0)
    except:
        pass
    
    dev.set_configuration()
    ifc = TUSB8044(dev)
    feature_report = ifc._get_report_feature()
    print("Got feature report value of {}".format(feature_report.tobytes()))
    
    
    #write 0xdeadbeef on i2c
    ifc.i2c_write(0x04, bytes([0xde, 0xad, 0xbe, 0xef]))


