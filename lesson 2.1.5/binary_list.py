class BinaryList(list):
    def __str__(self):
        return self._to_binary_string()

    def __repr__(self):
        return self._to_binary_string()

    def _to_binary_string(self):
        binary_str_list = []
        for item in self:
            if isinstance(item, bytes):
                binary_str_list.append('bits: ' + ''.join(f'{byte:08b}' for byte in item))
            else:
                binary_str_list.append(str(item))
        return '[' + ',\n'.join(binary_str_list) + ']'

    def __getitem__(self, index):
        result = super(BinaryList, self).__getitem__(index)
        if isinstance(index, slice):
            return BinaryList(result)
        return result