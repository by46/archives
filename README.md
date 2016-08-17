# Archives

Archives是一个文档自动构建及托管项目， 用于快速编写和维护项目文档。

## Prerequisites
- 文档必须使用[reStructuredText](http://docutils.sourceforge.net/rst.html)编写
- 文档需要位于/doc目录下
- 文档入口为/doc/index.rst

## Usage
1. 在trgit2上， 添加 [http://scmesos06/docs/dfis/archives/latest/index.html](http://10.16.76.248:9224/archives/hook)到项目的webhook中即可，
2. 通过[http://scmesos06/docs/<GROUP>/<PROJECT>/latest/index.html](http://scmesos06/docs/<GROUP>/<PROJECT>/latest/index.html)访问文档首页。例如：我有一个项目[http://trgit2/dfis/archives.git](http://trgit2/dfis/archives.git)，配置webhook之后，
如果有代码提交到了feature-doc，就会触发构建文档，我就可以通过[http://scmesos06/docs/dfis/archives/latest/index.html](http://scmesos06/docs/dfis/archives/latest/index.html)来访问文档。