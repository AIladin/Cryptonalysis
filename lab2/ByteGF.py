import numpy as np


class BitGF:
    def __init__(self, bits: np.array):
        assert len(bits) == 8, "Wrong byte length."
        self.bits = bits
        assert set(self.bits) == {True, False} or {True} or {False}, "Wrong byte structure."

    @classmethod
    def from_bytes(cls, byte_str: str):
        return cls(np.array(list(map(lambda x: x == '1', reversed(list(byte_str))))))

    @property
    def degree(self):
        return np.where(self.bits)[0][0]

    def __getitem__(self, item):
        return self.bits[item]

    def repr2(self):
        return ''.join((map(lambda x: '1' if x else '0', reversed(self.bits))))

    def __str__(self):
        if True in self.bits:
            return '+'.join([f"x^{i-1}" for i in range(len(self.bits), 1, -1) if self[i-1]]) +\
                   (f'+1' if self[0] else '')
        else:
            return "0"

    def __add__(self, other):
        return BitGF(np.logical_xor(self.bits, other.bits))

    @staticmethod
    def _reduce(this: np.array):
        p = [True, False, False, False, True, True, False, True, True]
        while True:
            if not any(this):
                return np.full(8, False)

            this = this[np.where(this)[0][0]:]

            if len(this) < 9:
                return np.concatenate((np.full((8 - len(this),), False), this))

            t = np.concatenate((p, np.full((len(this)-len(p),), False)))

            this = np.logical_xor(this, t)
            this = this[np.where(this)[0][0]:]

    def _naive_mul__(self, other):
        tmp = np.zeros(16, dtype='b')
        for x_d, x in enumerate(self):
            for y_d, y in enumerate(other):
                if x and y:
                    tmp[x_d + y_d] = np.logical_xor(tmp[x_d + y_d], 1)
        return tmp

    def logical_xor(self, other):
        return self*other

    def __mul__(self, other):
        c = self._reduce(self._naive_mul__(other)[::-1])
        return BitGF(c[::-1])

    def __pow__(self, power, modulo=None):
        if power == 0:
            return BitGF.from_bytes('00000001')

        result = BitGF.from_bytes('00000001')
        base = self
        while power > 0:

            if power % 2 == 0:
                power = power // 2
                base = base * base
            else:
                power = power - 1
                result = result * base

        return result

    def __invert__(self):
        if any(self.bits):
            return self**254
        else:
            return self

    def __eq__(self, other):
        return all(self.bits == other.bits)

    def repr16(self):
        return hex(int(self.repr2(), 2))[2:].zfill(2)

    def __repr__(self):
        return self.repr16()

    @classmethod
    def from_hex(cls, hex_str: str):
        return cls.from_bytes(bin(int(hex_str, 16))[2:].zfill(8))

    @classmethod
    def random(cls):
        return cls.from_bytes(bin(np.random.randint(0, 256))[2:].zfill(8))

    def compare(self, other):
        return np.sum(self.bits != other.bits)

class ByteGF:
    def __init__(self, byte_array: np.array):
        assert len(byte_array) == 4, f"Wrong byte array length: {len(byte_array)}, expected 4."
        self.bytes = byte_array
        assert all(isinstance(x, BitGF) for x in self.bytes), f"Wrong byte type."

    def __getitem__(self, item):
        return self.bytes[item]

    def __repr__(self):
        return ' '.join((*map(lambda x: x.repr16(), self.bytes),))

    def __str__(self):
        return '+'.join(f'[{self[i].repr16()}]x^{i}' for i in range(3, 0, -1) if any(self[i])) +\
               f'+[{repr(self[0].repr16())}]'

    def __add__(self, other):
        assert isinstance(other, ByteGF), "Can only add Bytes."
        res = []
        for i, j in zip(self, other):
            res.append(i+j)
        return ByteGF(res)

    def __mul__(self, other):
        a = np.concatenate([np.roll(self.bytes[::-1], i) for i in range(4)]).reshape((4, 4)).transpose()
        b = other.bytes
        return ByteGF(a.dot(b))

    def __pow__(self, power):
        x = self
        for i in range(power-1):
            print(x)
            x = self * x

        return x


if __name__ == '__main__':
    c = ByteGF(np.array([BitGF.from_hex('02'), BitGF.from_hex('01'), BitGF.from_hex('01'), BitGF.from_hex('03')]))
    print(c**255)
