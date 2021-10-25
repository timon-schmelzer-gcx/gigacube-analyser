# Configure a Small Server to Run Applications On
In the following lines you will learn how to set up a small home server to continuous
run applications on it. In my case, I used a Raspberry Pi 3 Model B (aka RPi). As I use a
Ubuntu image as OS, the performance of your server should not be significanlty slower
than my, otherwise things start to become annoyingly slow.

### Flash SSD Card
First, you need to flash the OS image on a SSD card. You can find the Ubuntu image
on their [official web site](https://ubuntu.com/download/raspberry-pi). For the flashing
I used the [Etcher](https://www.balena.io/etcher/) software, which is free and easy to use.
My SSD has 32GB, which is definitely sufficient for our use-cases.

### Enable SSH Access
Working physically on the server console is annoying. What we instead would
like to do is use our favourite laptop/desktop pc and connect to the server via SSH. On default,
the SSH deamon is disabled on the RPi. This means: connect power supply, keyboard, monitor and
ethernet cable to the RPi and log in. The default credentials are pi (user) and raspberry (password).
Note that the keyboard layout is american english, so the "y" and "z" positions are switched if you
are used to e.g. german layouts (as I am :)).

Once logged in, enable SSH access:

```bash
sudo systemctl enable ssh  # enable on restart
sudo systemctl start ssh  # start ssh deamon
```

Thats it. Everything else can be done via an SSH connection. Shut down the server via
`sudo shutdown now`, move it to it's final destination and connect it via ethernet.
For example, mine is located direclty at the main switch in the basement.

### Update OS and Simplify Login
Only an updated OS is an save OS. We can start the updating process by typing

```bash
sudo apt update
sudo apt full-upgrade
```

Be warned, this can take a few minutes. When it's done, we want to simplify the login
using authorisation the an SSH keypair. Doing so does not only increase security, we
also can omit typing our password every time we want to log in. Awesome! To generate a
SSH keypair, we can follow instructions from [here](https://bit.ly/3tPQP93).
As described in this tutorial, we also modify have to modify our .ssh/config accordingly.
Mine looks as follows:

```s
Host ed  # this means I can log in via `ssh ed`
  HostName 192.168.8.121
  User timon
  IdentityFile ~/.ssh/id_rpi_ed25519
```

Note that I added a new user with sudo rights and the name _timon_. I did so via the
command `sudo adduser timon sudo`. You can also keep the default user _ubuntu_ if you want.

On the server, create a new file and folder `~/.ssh/authorized_keys` and add the public key
(`~/.ssh/id_rpi_ed25519` in my case). You should now be able to log in with no password
required.

To further increase security, we can deactivate password access via SSH completely:

```
sudo vi /etc/ssh/sshd_config

# change inside file
PasswordAuthentication no
```

If you are a lazy person like me and you don't want to type your password on every `sudo`
command with your newly added user, have a look at [this SO answer](https://askubuntu.com/a/147265).

### Install software
For our applications we need a recent version of python 3 together with some
python libraries installed. There are about [256 different ways to install
python and manage its dependencies](https://xkcd.com/1987/), so feel free
to install it on your own. I did the following:

1. Installing miniconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-aarch64.sh
chmod +x Miniconda3-py39_4.9.2-Linux-aarch64.sh
./Miniconda3-py39_4.9.2-Linux-aarch64.sh
```
Note that by the time of writing this, the most recent version of Miniconda did not work for me. I received
the same error as in [this SO post](https://stackoverflow.com/questions/68099000/conda-init-illegal-instruction-core-dumped).

In principle, you could use Miniconda to create a new environment and start installing
dependencies. This would be a way to do it:

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict

conda create -n dashboard streamlit pandas
```

However, in my RPi 3 nothing happened for about 10 minutes and then I got an timeout error.
So I had to install another python dependencies manager, [poetry](https://python-poetry.org/).
I simply installed it into the `base` environment of Miniconda via

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Futhermore, I had to install some core dependencies using apt:

```
sudo apt install gcc
sudo apt install make
```

Finally we should be able to install all relevant software. In the repository folders you will find
the dependencies files `pyproject.toml`. To create an environment, switch to that folder (e.g. _dashboard_),
type `poetry install` to install everything and `poetry shell` to make this environment your default.
You should now be ready to run the code!

### Further configurations
It is always helpful to configure the tools and the system you work with. For git, we should add
a name and email:

```bash
git config --global user.name "Timon Schmelzer"
git config --global user.email timon.schmelzer@tu-dortmund.de
```

If you are not living in the UTC timezone, you should also modify the time zone correctly. I
live in Germany, so I switched the timezone in the following way:

```bash
sudo timedatectl set-timezone Europe/Berlin
```

If you do not like the hostname _ubuntu_, you can change it by editing
/etc/hostname (`sudo vi /etc/hostname`). Do not forget to reboot afterwards!

Furthermore, if you do not like to type ip addresses in your browser, you
can install and configure the _avahi-daemon_ to access the
dashboard like follows: `ubuntu.local:8501`.

### Automate services
This is the most tricky part in my opinion. Of course we could run the applications via
SSH terminals and everything will run fine. We could also use a terminal multiplexer
like [tmux](https://github.com/tmux/tmux) to detach our running session, which means
we could detech the session and close the terminal window. But what we actually want is
to have a service - something that automatically starts when we boot the OS and
can be simply stopped without interruption a running session. Luckily, _systemd_
provides an interface to accomplish exactly that.

For the streamlit dashboard, I added a `dashboard.service` file in the main folder.
This is the configuration file for the service. Please modify the paths in it accordingly.
Afterwards, run the following commands:

```
sudo cp dashboard.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

The service should now be running.

If you have a script that should run on a regular basis, like the web scraper in this repository,
we can use the [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html) scheduler.
Open a new file via `crontab -e` and add the following line (ensure the correcy path to the python
environment first):

```
* * * * * /home/timon/.cache/pypoetry/virtualenvs/scraper-omaoyfXU-py3.9/bin/scrapy crawl volume -o /home/timon/Code/scraper/data/volumes.jl > /dev/null 2>&1
```

This runs the command automatically every minute.
