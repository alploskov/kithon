def conf_get(file_name):
    sts=list(map(lambda s:s.replace('\n', '').split('='), open(file_name, 'r')))
    return {i[0]:i[1] for i in sts}
