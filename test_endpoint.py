#!/usr/bin/env python3
import json
import requests
import time

RUNPOD_API_KEY = 'INSERT_RUNPOD_API_KEY_HERE'
SERVERLESS_ENDPOINT_ID = 'INSERT_RUNPOD_ENDPOINT_ID_HERE'
RUNPOD_ENDPOINT_BASE_URL = f'https://api.runpod.ai/v2/{SERVERLESS_ENDPOINT_ID}'


def get_response_output(resp_json):
    result = resp_json['output']['results'][0]['history']

    if len(result['visible']):
        print(result['visible'][-1][1])
    else:
        print('No visible output received from endpoint')
        print(json.dumps(resp_json, indent=4, default=str))


if __name__ == '__main__':
    # Create the payload dictionary
    payload = {
        "input": {
            "user_input": "Please give me a step-by-step guide on how to plant a tree in my backyard."
        }
    }

    r = requests.post(
        f'{RUNPOD_ENDPOINT_BASE_URL}/runsync',
        headers={
            'Authorization': f'Bearer {RUNPOD_API_KEY}'
        },
        json=payload
    )

    print(f'Status code: {r.status_code}')

    if r.status_code == 200:
        resp_json = r.json()

        if 'output' in resp_json and 'results' in resp_json['output']:
            get_response_output(resp_json)
        elif 'output' in resp_json and 'errors' in resp_json['output']:
            print(f'ERROR: {json.dumps(resp_json["output"]["errors"], indent=4, default=str)}')
        else:
            job_status = resp_json['status']
            print(f'Job status: {job_status}')

            if job_status == 'IN_QUEUE' or job_status == 'IN_PROGRESS':
                request_id = resp_json['id']
                request_in_queue = True

                while request_in_queue:
                    r = requests.get(
                        f'{RUNPOD_ENDPOINT_BASE_URL}/status/{request_id}',
                        headers={
                            'Authorization': f'Bearer {RUNPOD_API_KEY}'
                        }
                    )

                    print(f'Status code from RunPod status endpoint: {r.status_code}')

                    if r.status_code == 200:
                        resp_json = r.json()
                        job_status = resp_json['status']

                        if job_status == 'IN_QUEUE' or job_status == 'IN_PROGRESS':
                            print(f'RunPod request {request_id} is {job_status}, sleeping for 5 seconds...')
                            time.sleep(5)
                        elif job_status == 'FAILED':
                            request_in_queue = False
                            print(f'RunPod request {request_id} failed')
                        elif job_status == 'CANCELLED':
                            request_in_queue = False
                            print(f'RunPod request {request_id} cancelled')
                        elif job_status == 'COMPLETED':
                            request_in_queue = False
                            print(f'RunPod request {request_id} completed')
                            get_response_output(resp_json)
                        elif job_status == 'TIMED_OUT':
                            request_in_queue = False
                            print(f'ERROR: RunPod request {request_id} timed out')
                        else:
                            request_in_queue = False
                            print(f'ERROR: Invalid status response from RunPod status endpoint')
                            print(json.dumps(resp_json, indent=4, default=str))
            elif job_status == 'COMPLETED' and 'errors' in resp_json['output']:
                print(f'ERROR: {json.dumps(resp_json["output"]["errors"], indent=4, default=str)}')
            else:
                print(json.dumps(resp_json, indent=4, default=str))
    else:
        print(f'ERROR: {r.content}')
