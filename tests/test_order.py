from unittest import TestCase

from importloc import Location, get_instances, get_subclasses, random_name, unload


# sample data


class Base(tuple[str]): ...


class Sample3(Base):
    """key = x"""


class Sample1(Base):
    """key = z"""


class Sample2(Base):
    """key = y"""


sample1 = Sample1('z')
sample2 = Sample2('y')
sample3 = Sample3('x')


# tests


class OrderInGetFunctions(TestCase):
    def setUp(self) -> None:
        self.module = Location('tests/test_order.py').load(random_name)
        self.Base: type[Base] = self.module.Base  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        unload(self.module)  # type: ignore

    # default order

    def test_instance_default_order(self) -> None:
        expected = [sample1, sample2, sample3]
        self.assertListEqual(expected, get_instances(self.module, self.Base))

    def test_subclasses_default_order(self) -> None:
        expected = ['Sample1', 'Sample2', 'Sample3']
        classes = get_subclasses(self.module, self.Base)
        self.assertListEqual(expected, [c.__name__ for c in classes])

    # name order

    def test_instance_name_order(self) -> None:
        expected = [sample1, sample2, sample3]
        objects = get_instances(self.module, self.Base, order='name')
        self.assertListEqual(expected, objects)

    def test_subclasses_name_order(self) -> None:
        expected = ['Sample1', 'Sample2', 'Sample3']
        classes = get_subclasses(self.module, self.Base, order='name')
        self.assertListEqual(expected, [c.__name__ for c in classes])

    # source order

    def test_instance_source_order(self) -> None:
        with self.assertRaises(TypeError):
            get_instances(self.module, self.Base, order='source')
        expected = [Sample3, Sample1, Sample2]
        all_types = get_instances(self.module, type, order='source')
        sample_types = [c for c in all_types if c.__name__.startswith('Sample')]
        self.assertListEqual(
            [c.__name__ for c in expected],
            [c.__name__ for c in sample_types],
        )

    def test_subclass_source_order(self) -> None:
        expected = ['Sample3', 'Sample1', 'Sample2']
        classes = get_subclasses(self.module, self.Base, order='source')
        self.assertListEqual(expected, [c.__name__ for c in classes])

    # custom order

    def test_instance_custom_order(self) -> None:
        expected = [sample3, sample2, sample1]
        objects = get_instances(self.module, self.Base, order=lambda o: o)
        self.assertListEqual(expected, objects)

    def test_subclass_custom_order(self) -> None:
        expected = ['Sample3', 'Sample2', 'Sample1']
        classes = get_subclasses(self.module, self.Base, order=lambda c: c.__doc__)
        self.assertListEqual(expected, [c.__name__ for c in classes])
