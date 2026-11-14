from itertools import product

from ic616.threshold import primitive_catalog


def test_primitive_catalog() -> None:
    catalog = primitive_catalog()
    for a, b in product((0, 1), repeat=2):
        assert catalog["AND2"]((a, b)) == (a & b)
        assert catalog["OR2"]((a, b)) == (a | b)
        assert catalog["NAND2"]((a, b)) == int(not (a & b))
        assert catalog["NOR2"]((a, b)) == int(not (a | b))
    for bit in (0, 1):
        assert catalog["NOT"]((bit,)) == int(not bit)
    for x in product((0, 1), repeat=3):
        assert catalog["MAJ3"](x) == int(sum(x) >= 2)
