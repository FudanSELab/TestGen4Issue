# TestGen4Issue
基于LLM和检索增强的故障复现测试用例生成方法，自动化为GitHub Issue生成故障复现测试用例。

![TestGen4Issue架构图](./images/TestGen4Issue.jpg)

## 方法简介

本工作为基于LLM和检索增强的故障复现测试用例生成方法，如上图所示，输入为一个GitHub Issue及其所在代码仓库，输出为复现Issue内容并验证Issue是否解决的故障复现测试用例。具体而言，本方法主要分为四个步骤：报错根函数定位、测试文件选择与import语句抽取、基于相似度计算的测试用例样本选取，以及最终的故障复现测试用例生成。通过这些步骤，本文方法有效获取了与Issue相关的上下文信息，并将其整合在prompt中，增强了大语言模型在故障复现测试用例生成中的表现。

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
