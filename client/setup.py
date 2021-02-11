from setuptools import setup, find_packages

setup(name="takmachat_client",
      version="0.0.1",
      description="client for small messaging application",
      author="Dmitry Takmakov",
      author_email="dj-dat@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
