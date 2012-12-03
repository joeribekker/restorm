import oauth2 as oauth

from unittest2 import TestCase, skipIf

from restorm.examples.twitter import api

try:
    from settings_local import TWITTER_SETTINGS
except ImportError:
    TWITTER_SETTINGS = None


class TwitterLiveTests(TestCase):
    
    def setUp(self):
        consumer = oauth.Consumer(key=TWITTER_SETTINGS['CONSUMER_KEY'], secret=TWITTER_SETTINGS['CONSUMER_SECRET'])
        token = oauth.Token(key=TWITTER_SETTINGS['TOKEN_KEY'], secret=TWITTER_SETTINGS['TOKEN_SECRET'])

        self.client = api.TwitterClient(consumer, token)
    
    @skipIf(TWITTER_SETTINGS is None, 'You must provide "TWITTER_SETTINGS" in your "settings_local.py". See: "settings_local_example.py".')
    def test_search(self):
        search_results = api.TwitterSearch.objects.all(query={'q': 'python'}, client=self.client)
        self.assertTrue(search_results['search_metadata']['count'] > 0, 'No search results on Python? This cannot be correct!')
        self.assertEqual(len(search_results['statuses']), search_results['search_metadata']['count'])

    @skipIf(TWITTER_SETTINGS is None, 'You must provide "TWITTER_SETTINGS" in your "settings_local.py". See: "settings_local_example.py".')
    def test_tweet(self):
        tweet_list = api.TwitterTweet.objects.all(query={'screen_name': TWITTER_SETTINGS['SCREEN_NAME']}, client=self.client)
        self.assertTrue(len(tweet_list) > 0, 'You need to have some tweets.')
        tweet_item = api.TwitterTweet.objects.get(id=tweet_list[0]['id'], client=self.client)
        self.assertEqual(tweet_list[0]['text'], tweet_item.data['text'])
