# GenRandomFiles Plugin

This plugin generates arbitrary amount of random files without creating them on disk. The purpose is to fill the Bareos catalog database eg. for testing or benchmarking.

## Prerequisites

You need the package bareos-filedaemon-python2-plugin or bareos-filedaemon-python3-plugin  installed on your client.

## Configuration

### Enable Python Plugins in your bareos-fd Configuration

See https://docs.bareos.org/TasksAndConcepts/Plugins.html#python-plugins

### Configure a FileSet that uses the plugin
```
FileSet {
  Name = "Data1Set"
  Include {
    Options {
      signature = SHA1
    }
    Plugin = "python:module_path=/usr/lib64/bareos/plugins:module_name=bareos-fd-gen-random-files:levels=10,10,10,1000:topdir=/data/1"
  }
```

The above example will create 1 million random files, with 3 levels of directories below `/data/1`, for example

```
/data/1/9-Zi2Tk56oaJqclLm/6-EpWyHLZ2mMuG9GVie7aEVJ64hQZuY/7-IIfNA7SY4iqldzVg4BGqwVb0n3uk5FYpF/0MEPX97hXXNoM
```

#### Options ####

With `levels=10,10,10,1000` the plugin will create `10*10*10 = 1000` directories each with 1000 files.
