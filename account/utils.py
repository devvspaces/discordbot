import random, string


def random_text(p=5):
    return ''.join(random.sample(string.ascii_uppercase + string.digits,p))

def unique_name(instance, discord_username=None, length=5):
    if not discord_username:
        code=random_text(length)
        discord_username = f'USER-{code}'
    
    exists = instance.__class__.objects.filter(discord_username = discord_username).exists()
    
    if exists:
        return unique_name(instance)
    
    return discord_username