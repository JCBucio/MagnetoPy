# Environment Manual

---
## Prepare the work environment

### Install Python
You can download Python from the official website [Python](https://www.python.org/downloads/).

> **Note**: MagnetoPy supports Python 3.11.0 or higher.

---

### Install Git
You can download Git from the official website [Git](https://git-scm.com/downloads).

---

### Install PyCharm
You can download PyCharm from the official website [PyCharm](https://www.jetbrains.com/pycharm/download/).
I recommend using the Community version because it is free and has all the necessary tools to work with MagnetoPy.

---

### Clone the repository
You can clone the repository using the following command:

```sh
git clone https://github.com/JCBucio/MagnetoPy.git
```

> **Note**: You can also download the repository as a zip file from the GitHub page but cloning the repository is recommended because you can easily update the repository with the latest changes using the command `git pull` (explained in the update repository step).

---

### Open the project in PyCharm
1. Open PyCharm.
2. Click on `Open`.
3. Select the MagnetoPy folder where you cloned the repository.
4. Copy the `runConfigurations` folder from the repository to the `.idea` folder in the project.

> **Note**: If the `.idea` folder does not appear in the project files, you can try closing the project and opening it again.

---

### Create a virtual environment
There are two ways to create a virtual environment for the project:

#### Using PyCharm

1. Open the project in PyCharm.
2. Click on `File` > `Settings`.
3. In the settings window, click on `Project: MagnetoPy` > `Python Interpreter`.
4. Click on the gear icon and select `Add`.
5. In the new window, select `Virtualenv Environment`.
6. In the `Location` field, enter the path where you want to create the virtual environment (I recommend creating the virtual environment in the project folder).
7. Click on `OK`.

#### Using the terminal

1. Open the terminal in PyCharm or use the terminal of your operating system.
2. Run the following command to create the virtual environment in the project folder:

```sh
python -m venv venv
```

Where `venv` is the name of the virtual environment. You can use any name you want.

---

### Install the project dependencies

There are two ways to install the project dependencies:

#### Using PyCharm

1. Open the project in PyCharm.
2. Open the `requirements.txt` file in the project.
3. Click on the `Install requirements` link that appears at the top of the file.

#### Using the terminal

1. Activate the virtual environment:

```sh
source venv/bin/activate
```

2. Run the following command to install the project dependencies:

```sh
pip install -r requirements.txt
```

> **Note**: I highly recommend using PyCharm either you are a beginner or an expert because it has all the necessary tools to work with Python projects.

---

### Update the repository

To update the repository with the latest changes, you can use the following command:

```sh
git pull origin main
```

> **Note**: Go to the `requirements.txt` file and install the new dependencies if necessary.

---

### Edit the run configurations

1. Open Edit Configurations in PyCharm.
    - Script path should be: <repository_path>\magnetopy.py
    - Parameters: See the section `Available commands in magnetopy-cli` in the HOW_TO_USE.md file.
    - Python interpreter: Select the virtual environment you created.
    - Modify options: Select the `Run with Python Console` option from the drop-down menu in the `Modify options` section.

---

### More resources
If the process of setting up the environment is not so clear, you can check the following resources:
- [MagnetoPy post](https://jcbucio.github.io/portafolio/MagnetoPy)

I'm working on a MagnetoPy video tutorial series to help you set up the environment and use the CLI. Stay tuned for updates!

If you have any questions or need help, you can contact me at [jcbucio.geo@gmail.com](mailto:jcbucio.geo@gmail.com).