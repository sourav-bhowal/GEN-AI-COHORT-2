#!/bin/bash

export $(grep -v '^#' .env | xargs -d '\n')
rq worker --with-scheduler --url redis://valkey-queue:6379