from setuptools import setup, find_packages

setup(
    name='melk.util',
    version="0.1",
    description="General utilities used by melkjug",
    author="Luke Tucker",
    author_email="ltucker@openplans.org",
    #url="",
    install_requires=[
    ],
    dependency_links=[
    ],
    packages=find_packages(),
    namespace_packages=['melk'],
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [console_scripts]
    melk_hash = melk.util.hash:main
    """,
)
