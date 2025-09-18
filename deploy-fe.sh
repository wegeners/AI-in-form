#!/bin/bash
cd frontend
aws s3 sync . s3://ai-in-form-aiinformw-458650368656 --delete
