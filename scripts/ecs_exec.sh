aws ecs execute-command --cluster $CLUSTER_NAME \
    --task $TASK_ARN \
    --container gunicorn \
    --interactive \
    --command "/bin/bash"