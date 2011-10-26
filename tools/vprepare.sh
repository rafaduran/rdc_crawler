#!/usr/bin/env bash

echo "deb http://download.virtualbox.org/virtualbox/debian maverick contrib non-free" > /etc/apt/sources.list.d/virtual_box_maverick.list
wget http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc
apt-key add oracle_vbox.asc
apt-get update
apt-get install -y virtualbox-4.1 ruby1.8-dev rubygems1.8 libruby1.8 ruby1.8 rubygems1.8 --force-yes
gem install vagrant

