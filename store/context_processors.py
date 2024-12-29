
def breadcrumbs_processor(request):
    path = request.path.strip('/').split('/')
    breadcrumbs = [{'url': '/', 'label': 'Home'}]
    for i in range(len(path)):
        url = '/' + '/'.join(path[:i + 1]) + '/'
        label = path[i].replace('-', ' ').capitalize()
        breadcrumbs.append({'url': url, 'label': label})
    return {'breadcrumbs': breadcrumbs}
