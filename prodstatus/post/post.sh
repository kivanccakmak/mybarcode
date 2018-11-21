#!/bin/bash

while [ true ]; 
do
    python post.py record.json http://127.0.0.1:9191/upload
    sleep 6
done
