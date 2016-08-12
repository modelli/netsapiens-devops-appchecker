#!/usr/bin/env bash

_MAILTO="4697347002@txt.att.net"

_MID=125
_HIGH=145
_SPIKE=15

_TIMER=10

_OK="Ok"
_WARNING="Warning above $_MID"
_BROKEN="Broken above $_HIGH"
_DOWN="No process found"

_MODE=$_OK
_LMODE=$_OK

_LAST=0

while [ y ]; do
        _NOW=`ps auxww | grep apache2 | wc -l`

        let "_JUMP = $_NOW - $_LAST"

        _MSIPKE=false
        _MCHANGE=false

        if [ $((_NOW)) == "0" ]; then
                _MODE=$_DOWN
        else
                if [ $((_JUMP)) -gt $((_SPIKE)) ]; then
                        _MSPIKE=true
                else
                        _MSPIKE=false
                fi

                if [ $((_NOW)) -gt $((_HIGH)) ]; then
                        _MODE=$_BROKEN
                elif [ $((_NOW)) -gt $((_MID)) ]; then
                        _MODE=$_WARNING
                else
                        _MODE=$_OK
                fi
        fi

        if [ "$_MODE" != "$_LMODE" ]; then
                _MCHANGE=true
                _MSG="Mode changed from \"$_LMODE\" to \"$_MODE\""
        else
                _MSG="No mode change"
        fi

        if [ $_MSPIKE == true ]; then
                [ $_LAST -ne 0 ] && [ $_JUMP -gt 0 ] && [ $_LSPIKE == true ] && _MCHANGE=true && echo "SPINKING $_SPIKE:$_JUMP"
                _MSG="$_MSG WITH spike"
        else
                _MSG="$_MSG WITHOUT spike"
        fi

        [ $_MCHANGE == true ] && {
                _LSB=`lsb_release -d`
                _HOSTNAME=`hostname -a`
                _STATUS="$_LAST:$_NOW:$_JUMP"
                _MSG="$_HOSTNAME\n$_LSB\n$_MSG: $_STATUS"
                echo -e "$_MSG" | sendmail $_MAILTO
                if [ $? -eq 0 ]; then
                        echo "EMAIL SENT WITH:\n $_MSG"
                else
                        echo "EMAIL FAILED WITH::\n $_MSG"
                fi
        } || {
                echo "$_MSG: $_LAST:$_NOW:$_JUMP"
        }

        (( _LAST = _NOW ))
        _LMODE="$_MODE"
        _LSPIKE="$_MSPIKE"
        sleep $_TIMER
done
