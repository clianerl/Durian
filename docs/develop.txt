开发指南：
    1、参考/docs/tree.md了解项目结构
    2、参考/docs/config.md、/docs/rule.md了解规则配置
    3、扫描逻辑：
        durian是程序入口
        __init__.py命令行参数解析、调用cli扫描。
        cli.py 代码扫描
        ...
    4、如果要用到clang解析AST(Abstract Syntax Tree)抽象语法树，可以参考/test/test_clang
    5、如果需要添加其他缺陷扫描
           1)、可以调试一下代码，看一下程序的整体执行流程
           2)、在rules添加相应的缺陷检查规则
           3)、在cli下添加相应的检查逻辑，建议将检查逻辑功能写到engine.py。