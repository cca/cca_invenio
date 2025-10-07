# Building Invenio

Meaning both the docker build but also creating a local virtual environment with all the correct python requirements.

This document is mostly about errors you might encounter and resolving them.

## invenio-saml, python-xmlsec, uwsgi, & C libraries

The python XML ecosystem is a compatibility mess. We need it to use SSO authentication with `invenio-saml`, which depends on `python-xmlsec` (the source of most problems), which depends on `lxml`, and those both rely on the `libxml2` C library. Python's xmlsec also depends on `libxmlsec1`. lxml 5 [requires](https://lxml.de/installation.html#requirements) libxml2 2.9.2 or later and xmlsec 1.3 [requires](https://github.com/xmlsec/python-xmlsec?tab=readme-ov-file#requirements) libxml2 >= 2.9.1 & libxmlsec1 >= 1.2.33. If their libxml2 versions do not match, `import xmlsec` throws an exception. They both come with their own internally packaged versions of these libraries, which can be overridden by telling `uv` to skip binaries installs like `uv sync --no-binary-package lxml --no-binary-package xmlsec lxml==5.2.1 xmlsec==1.3.14`. Sometimes the binaries are incompatible with system libraries so this helps, though it was not the solution for us.

`invenio-saml` has no upper cap on its dependency constraints, which means it installs lxml 6 out of the box, which doesn't work at all. So we have to pin `lxml` and `xmlsec` in such a way that their underlying libraries match. The included libxml2 is 2.12.6 for `lxml==5.2.1` and `xmlsec==1.3.14`, while `lxml==5.3.0` uses `libxml2` 2.12.9 which works but after all these problems we are being conversative.

**Note**: [python-xmlsec==1.3.16](https://github.com/xmlsec/python-xmlsec/releases/tag/1.3.16) claims to work with lxml 6 so that might allow us to unpin and simplify our dependencies. This hasn't been tested.

| Works? | OS     | libxml2   | libxmlsec1   | lxml   | python-xmlsec |
|--------|--------|-----------|--------------|--------|---------------|
| ✅     | MacOS  | system 2.9? | brew 1.2.37 | 5.3.0  | 1.3.14        |
| ✅     | MacOS  | brew 2.13.8 | brew 1.3.7  | 5.4    | 1.3.15        |
| ✅     | Debian | 2.9.14    | 1.2.37-2     | 5.2.1  | 1.3.14        |
| ✅     | Debian | 2.9.14    | 1.2.37-2     | 5.3    | 1.3.14        |
| ❌     | Debian | 2.9.14    | 1.2.37-2     | 5.4    | 1.3.14        |
| ❓     | Debian | 2.9.14    | 1.2.37-2     | 5.4    | 1.3.15        |

We could probably upgrade to 5.4/1.3.15 but so much time has been spent on this issue already. View underlying libraries like so:

```python
from lxml import etree
print("lxml version:", etree.LXML_VERSION)
print("libxml2 version:", etree.LIBXML_VERSION)
import xmlsec # though this import fails if libraries are mismatched
print(
    "xmlsec version", xmlsec.__version__,
    "libxml version", xmlsec.get_libxml_version(),
    "libxml compiled version", xmlsec.get_libxml_compiled_version(),
    "libxmlsec version", xmlsec.get_libxmlsec_version(),
)
```

### Debian

When running the app's Linux image we saw a [XML library mismatch error](https://github.com/cca/cca_invenio/issues/39) during `import xmlsec`. However, running `python -c "import xmlsec"` works. The problem only occurs when running the app under the `uwsgi` server. I tried many fixes, noted in the issue, but eventually deduced that `uwsgi` builds with incompatible libraries which somehow filter down to `xmlsec`. The installed versions of the two python packages (whether installed with binary or without) and system libraries do not matter. The `uwsgi` server must be built with the `xml=no` profile override (see [this comment](https://github.com/xmlsec/python-xmlsec/issues/320#issuecomment-2451246797)).

## macOS

Challenges with building or running Invenio locally.

### celery on macOS 26 Tahoe

Issue [celery/celery#9894](https://github.com/celery/celery/issues/9894) causes various background workers to crash continually when running locally. As mentioned on the thread, the solution is to not use the default celery `prefox` pool but anything else, so we set `CELERY_WORKER_POOL = "threads"` in [mise.toml](../mise.toml). The `NOSETPS` env var seemed to improve stability but not stop crashes.

### xmlsec

The new macOS chips & python's SAML/XML libraries don't work well together. In running Invenio locally with `invenio-saml`, the app would crash with an error from the xmlsec dependency:

```python
    File ".venv/lib/python3.12/site-packages/onelogin/saml2/auth.py", line 12, in <module>
    import xmlsec
ImportError: dlopen(.venv/lib/python3.12/site-packages/xmlsec.cpython-312-darwin.so, 0x0002):
symbol not found in flat namespace '_xmlSecOpenSSLTransformHmacRipemd160GetKlass'
```

Pinning python-saml's dependencies to specific versions (lxml==5.3.0, xmlsec==1.3.14) fixed the issue. The saml library is loose with its dependency constraints ("lxml>=4.6.5,!=4.7.0", "xmlsec>=1.3.9") as is xmlsec ("lxml>=3.8, !=4.7.0"). It may also be necessary to use an older libxmlsec1 in homebrew (I used 1.2.37 from [my own tap](https://github.com/phette23/homebrew-local)). There's discussion of this issue in python-xmlsec bugs [163](https://github.com/xmlsec/python-xmlsec/issues/163), [254](https://github.com/xmlsec/python-xmlsec/issues/254), and [346](https://github.com/xmlsec/python-xmlsec/issues/346). [This comment](https://github.com/xmlsec/python-xmlsec/issues/163#issuecomment-2766043196) discusses the same fix but `--no-binary` flag not been necessary.

Example of building against homebrew libraries:

```sh
# fish shell
set XMLSEC1_DIR (brew --prefix libxmlsec1)
set XML2_DIR (brew --prefix libxml2)
# shouldn't brew link libxml2 be enough?
ln -sf $XML2_DIR/lib/libxml2.2.dylib /opt/homebrew/lib/libxml2.2.dylib
set -x CFLAGS -I$XML2_DIR/include/libxml2 -I$XMLSEC1_DIR/include/xmlsec1
set -x DYLD_LIBRARY_PATH $XMLSEC1_DIR/lib $XML2_DIR/lib/pkgconfig/lib
set -x LDFLAGS -L$XML2_DIR/lib -L$XMLSEC1_DIR/lib
set -x PATH $XMLSEC1_DIR/bin $PATH
set -x PKG_CONFIG_PATH $XMLSEC1_DIR/lib/pkgconfig $XML2_DIR/lib/pkgconfig
uv pip uninstall xmlsec
uv sync --reinstall
# check linked library and versions
otool -L .venv/lib/python3.12/site-packages/xmlsec*.so
uv run python -c "import xmlsec; print(xmlsec.__version__, xmlsec.get_libxml_version(), xmlsec.get_libxml_compiled_version(), xmlsec.get_libxmlsec_version())"
```

### uwsgi

If we run Invenio locally with the `invenio-cli run` command, which uses flask's debugging web server, we should not need `uwsgi`. For this reason, `uwsgi` is in a separate dependency group in our [pyproject.toml](../pyproject.toml) and must be synced with `uv sync --group uwsgi`.

Anytime you install or rebuild `uwsgi` on macOS, it tends to fail because uwsgi needs to know the path to the current python environment and not the system one. Errors might say something like `ld: warning: search path '/install/lib' not found`, `ld: library 'python3.12' not found`, `clang: error: linker command failed with exit code 1 (use -v to see invocation)`, etc.

See [this comment](https://github.com/astral-sh/uv/issues/6488#issuecomment-2345417341) for instance. The solution is to set a `LIBRARY_PATH` env var that points to the "lib" directory of our local python. With `mise` and fish shell, this looks like `set -x LIBRARY_PATH (mise where python)/lib`.

## invenio-cli install & cairo

I've run into `invenio-cli install` build errors related to the cairo package, the errors say something like "no library called "cairo" was found" and "cannot load library 'libcairo.2.dylib'". I had cairo installed via homebrew, but the library wasn't in any of the directories that the build process was looking in. I fixed this with `ln -sf (brew --prefix cairo)/lib/libcairo.2.dylib /usr/local/lib/` (the path to the cairo library may be different on your system).
