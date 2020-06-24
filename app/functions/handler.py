import curlapi


def get_joke_from_layer(event, context):
    it_worked = curlapi.get_dad_joke('https://geek-jokes.sameerkumar.website/api')
    return it_worked
