#!/bin/bash

uv run {{ package_name.split('.')[-1] }} "$@"
