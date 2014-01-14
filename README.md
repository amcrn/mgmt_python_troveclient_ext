=============================
mgmt_python_troveclient_ext
=============================

Management API extensions for python-troveclient (v1.0+).

Setup:

```
$ git clone git://github.com/openstack/python-troveclient.git
$ git clone git://github.com/amcrn/mgmt_python_troveclient_ext.git
$ cd python-troveclient
$ pip install -r requirements.txt
$ python setup.py develop
# fetch extensions fix, see https://review.openstack.org/#/c/65758/
$ git fetch https://review.openstack.org/openstack/python-troveclient refs/changes/58/65758/4 && git cherry-pick FETCH_HEAD
$ cd ../mgmt_python_troveclient_ext
$ python setup.py develop
$ trove
```
