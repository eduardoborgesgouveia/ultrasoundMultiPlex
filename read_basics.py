import struct
import time


possible_codecs = [
    "ascii",
    "big5",
    "big5hkscs",
    "cp037",
    "cp424",
    "cp437",
    "cp500",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "cp1006",
    "cp1026",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "euc_jp",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_kr",
    "gb2312",
    "gbk",
    "gb18030",
    "hz",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "latin_1",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "iso8859_10",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "johab",
    "koi8_r",
    "koi8_u",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "ptcp154",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
    "utf_8_sig",
    "base64_codec",
    "bz2_codec",
    "hex_codec",
    "idna",
    "mbcs",
    "palmos",
    "punycode",
    "quopri_codec",
    "raw_unicode_escape",
    "rot_13",
    "string_escape",
    "undefined",
    "unicode_escape",
    "unicode_internal",
    "uu_codec",
    "zlib_codec",
]


def ler_primeiras_linhas(n):
    with open("0-p1.urec", "rb") as f:
        data = f.readlines()

    for i in range(n):
        print(data[i])
        print("\n\n")


def decode_teste_string(texto):
    for codec in possible_codecs:
        try:
            aux = texto.decode(codec)
            print("codec: ", codec)
            print("texto: ", aux)
            print("\n\n")
            # time.sleep(5)
        except Exception as e:
            # print("error: ", e)
            pass


def decode_lines():
    with open("0-p1.urec", "rb") as f:
        data = f.readlines()
    for line in data:
        for codec in possible_codecs:
            try:
                aux = line.decode(codec)
                print("codec: ", codec)
                print("texto: ", aux)
                print("\n\n")
                # time.sleep(5)
            except Exception as e:
                # print("error: ", e)
                pass


def decode_todo_arquivo():
    with open("0-p1.urec", "rb") as f:
        data = f.read()
    for codec in possible_codecs:
        try:
            aux = data.decode(codec)
            print("texto: ", aux[-5000:])
            print("codec: ", codec)
            print("\n\n")
            input("Press Enter to continue...")
        except Exception as e:
            # print("error: ", e)
            pass


def ler_arquivo_codecs():
    for codec in possible_codecs:
        try:
            with open("0-p1.urec", encoding=codec) as f:
                data = f.read()[-500:]
            print("texto: ", data)
            print("codec: ", codec)
            print("\n\n")
            input("Press Enter to continue...")
        except Exception as e:
            pass


def tentativa_palpite():
    file = open("0-p1.urec", "rb")
    s = file.read(8)
    addr, ts = struct.unpack(">II", s)
    print(addr)
    print(ts)


def ler_todo_arquivo_original():
    with open("0-p1.urec", "rb") as f:
        data = f.read()
    print(data)


def ler_parte_arquivo_original(start, quantidade):
    with open("0-p1.urec", "rb") as f:
        f.seek(start)
        data = f.read(quantidade)
    for codec in possible_codecs:
        try:
            aux = data.decode(codec)
            print("texto: ", aux)
            print("codec: ", codec)
            print("\n\n")
            input("Press Enter to continue...")
        except Exception as e:
            # print("error: ", e)
            pass


if __name__ == "__main__":
    # ler_primeiras_linhas(1)
    # ler_arquivo_codecs()
    # decode_teste_string(
    #     b"\xe6\x0c\x00\x00\x01\x00\x00\x00\x12\x00\x00\x00\r\x00\x00\x00\x04\x00\x00\x00X\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xe7\x07\x00\x00\x01\x00\x00\x00\x12\x00\x00\x00\x03\x00\x00\x00;\x00\x00\x008\x00\x00\x00\x9c\xd4\x1e\x00f[\x03\x00@\x01\x00\x00\x8d5\x03\x00\t\n"
    # )
    # tentativa_palpite()
    # ler_todo_arquivo_original()
    ler_parte_arquivo_original(2051, 6985)
