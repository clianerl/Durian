规则文件书写：

    1、CVI-100XXX.xml:
        1)、标签：
            <name/> :   规则名字
            <language/> :   规则语言
            <match/> :   规则匹配正则表达式, 属性：mode 匹配模式(暂未使用)
            <level/> :   规则等级
            <test/> :    测试用例
            <solution/> :   解决方案
            <status/> :   状态(暂未使用)
            <author/> :   开发者

        2)、模版
        <?xml version="1.0" encoding="UTF-8"?>
        <durian document="https://github.com/DurianCoder/Durian">
            <name value="Java接口声明的函数没有文档注释"/>
            <language value="java"/>
            <match mode="regex-only-match"><![CDATA[.*abstract.*\(.*\).*;$]]></match>
            <level value="2"/>
            <test>
                <case assert="true"><![CDATA[MedicalCard queryMedicalCardByPatientId(Number patientId) throws Exception;]]></case>
                <case assert="true"><![CDATA[List<PatientRegistEntity> queryPatientRegistByPatientIdAndDate(Number patientId, String registTime) throws Exception;]]></case>
            </test>
            <solution>
                ## 安全风险
                JAVA接口声明的函数没有写文档注释，不方便阅读和维护。
                ## 修复方案
                添加相应的文档注释。
            </solution>
            <status value="on"/>
            <author name="jy" email="jiangying1110@outlook.com"/>
        </durian>


    2、languages.xml
         1)、标签：
            <language/> :   规则语言
                chiefly：是否是主要语言
                <extension/>  语言后缀
        2)、模版

            <?xml version="1.0" encoding="UTF-8"?>
            <durian document="https://github.com/DurianCoder/Durian">
                <language name="*">
                    <extension value=".*"/>
                </language>
                <language name="Python" chiefly="true">
                    <extension value=".py"/>
                </language>
                <language name="C">
                    <extension value=".h"/>
                    <extension value=".c"/>
                </language>
                <language name="C++">
                    <extension value=".c"/>
                    <extension value=".h"/>
                    <extension value=".cpp"/>
                </language>

                <!-- 下面是自定义语言 -->
                <!-- 伪代码 ls-->
                <language name="ls">
                    <extension value=".logicservice"/>
                </language>
            </durian>


    3、vulnerabilities.xml
     1)、标签：
        <vulnerability/> :   缺陷
            name：缺陷名词
            vid:  缺陷ID
     2)、模版

        <?xml version="1.0" encoding="UTF-8"?>
        <durian document="https://github.com/DurianCoder/Durian">
            <vulnerability name="没有打印日志" vid="100"/>
            <vulnerability name="接口没有注释" vid="110"/>
            <vulnerability name="变量重复赋值" vid="120"/>
            <vulnerability name="变量重复赋值" vid="200"/>
        </durian>