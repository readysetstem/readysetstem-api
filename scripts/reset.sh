#!/bin/bash

sudo rm -rf /root/readysetstem_projects/*
sudo find /home/pi/rstem/projects/demos -name *.py -exec cp {} /root/readysetstem_projects \;
sudo find /home/pi/rstem/projects/demos -name *.spr -exec cp {} /root/readysetstem_projects \;

