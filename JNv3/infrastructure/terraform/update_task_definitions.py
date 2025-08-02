#!/usr/bin/env python3
import json
import sys

def update_backend_task_def():
    try:
        with open('backend-task-def.json', 'r') as f:
            task_def = json.load(f)
        
        # 更新镜像 URL 为 fixed 版本
        for container in task_def['containerDefinitions']:
            if container['name'] == 'backend':
                container['image'] = '039444453392.dkr.ecr.us-east-1.amazonaws.com/jobquest-navigator-v3-backend:fixed'
        
        # 移除不需要的字段
        fields_to_remove = ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 
                           'placementConstraints', 'compatibilities', 'registeredAt', 'registeredBy']
        for field in fields_to_remove:
            task_def.pop(field, None)
        
        with open('backend-task-def-new.json', 'w') as f:
            json.dump(task_def, f, indent=2)
        
        print('Backend task definition updated successfully')
    except Exception as e:
        print(f'Error updating backend task definition: {e}')
        sys.exit(1)

def update_frontend_task_def():
    try:
        with open('frontend-task-def.json', 'r') as f:
            task_def = json.load(f)
        
        # 更新镜像 URL 为 fixed 版本
        for container in task_def['containerDefinitions']:
            if container['name'] == 'frontend':
                container['image'] = '039444453392.dkr.ecr.us-east-1.amazonaws.com/jobquest-navigator-v3-frontend:fixed'
        
        # 移除不需要的字段
        fields_to_remove = ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 
                           'placementConstraints', 'compatibilities', 'registeredAt', 'registeredBy']
        for field in fields_to_remove:
            task_def.pop(field, None)
        
        with open('frontend-task-def-new.json', 'w') as f:
            json.dump(task_def, f, indent=2)
        
        print('Frontend task definition updated successfully')
    except Exception as e:
        print(f'Error updating frontend task definition: {e}')
        sys.exit(1)

if __name__ == "__main__":
    update_backend_task_def()
    update_frontend_task_def()