# Copyright (C) 2007 The Open Planning Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

from setuptools import setup, find_packages

setup(
    name='melk.util',
    version="0.5",
    description="General utilities used by melkjug",
    license="GPLv2 or any later version",
    author="Luke Tucker",
    author_email="ltucker@openplans.org",
    url="http://melkjug.openplans.org",
    install_requires=[
     "httplib2",
     "simplejson<2.0"
    ],
    dependency_links=[
      "https://svn.openplans.org/melk/eggs/links.html",
    ],
    packages=find_packages(),
    namespace_packages=['melk', 'melk.util'],
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [console_scripts]
    melk_hash = melk.util.hash:main
    """,
)

