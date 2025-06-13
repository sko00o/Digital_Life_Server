import logging
import os
import time

import GPT.tune as tune

from openai import OpenAI
import httpx


class GPTService():
    def __init__(self, args):
        logging.info('Initializing ChatGPT Service...')

        self.tune = tune.get_tune(args.character, args.model)

        self.counter = 0

        self.brainwash = args.brainwash

        # Configure proxy if provided
        http_client = None
        if hasattr(args, 'proxy') and args.proxy:
            logging.info(f'Using proxy: {args.proxy}')
            http_client = httpx.Client(
                proxies=args.proxy,
                timeout=httpx.Timeout(30.0, connect=10.0)
            )

        self.client = OpenAI(
            api_key=args.APIKey,
            base_url=args.APIBase,
            http_client=http_client
        )
        self.model = args.model
        logging.info('OpenAI API initialized.')

    def ask(self, text):
        stime = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.tune},
                {"role": "user", "content": text}
            ]
        )
        prev_text = response.choices[0].message.content

        logging.info('ChatGPT Response: %s, time used %.2f' %
                     (prev_text, time.time() - stime))
        return prev_text

    def ask_stream(self, text):
        prev_text = ""
        complete_text = ""
        stime = time.time()
        self.counter += 1

        data_source = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.tune},
                {"role": "user", "content": text}
            ],
            stream=True
        )

        for data in data_source:
            if data.choices[0].delta.get('content'):
                message = data.choices[0].delta.content
            else:
                continue

            if ("。" in message or "！" in message or "？" in message or "\n" in message) and len(complete_text) > 3:
                complete_text += message
                logging.info('ChatGPT Stream Response: %s, @Time %.2f' %
                             (complete_text, time.time() - stime))
                yield complete_text.strip()
                complete_text = ""
            else:
                complete_text += message

            prev_text += message

        if complete_text.strip():
            logging.info('ChatGPT Stream Response: %s, @Time %.2f' %
                         (complete_text, time.time() - stime))
            yield complete_text.strip()
