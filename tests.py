from functions.write_file import write_file


def test():
    result = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    print("Result for writing to 'lorem.txt' file:")
    print(result)
    print("")

    result = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    print("Result for writing to 'pkg/morelorem.txt' file:")
    print(result)
    print("")

    result = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    print("Result for writing to '/tmp/temp.tx' file:")
    print(result)
    print("")


if __name__ == "__main__":
    test()
