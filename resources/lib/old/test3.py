
class C:
    @staticmethod
    def test( slide=1 ):
        count += slide
        print count


C.test()
C.test(0)
C.test(-1)

    