from setuptools import find_packages, setup

with open("version") as fd:
    version = fd.read().strip()

with open("README.md") as f:
    README = f.read()


def _load_requirements(filename):
    with open(filename) as fd:
        reqs = [dependency.strip() for dependency in fd if dependency.strip()]
    return [r for r in reqs if not r.startswith("file://")]


requirements = _load_requirements("function/requirements.txt")
dev_requirements = _load_requirements("requirements-dev.txt")
test_requirements = _load_requirements("tests/requirements-test.txt")

setup_args = {
    "python_requires": ">=3.8",
    "name": "sendmail_cloud_function",
    "version": version,
    "description": "Send mail from a PubSub event",
    "long_description": README,
    "long_description_content_type": "text/markdown",
    "author": "Scott Houseman",
    "author_email": "scott@houseman.co.za",
    "url": "https://github.com/houseman/sendmail-cloud-function",
    "packages": find_packages(),
    "install_requires": requirements,
    "extras_require": {"dev": dev_requirements, "test": test_requirements},
    "test_suite": "tests",
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
}

setup(**setup_args)
