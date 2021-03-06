from werkzeug.datastructures import Headers


def tags_to_csv(json_data):
    flat_dict = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        else:
            flat_dict[name[:-1]] = x

    field_names = []
    for tx in json_data:
        flatten(tx)
        if not field_names:
            field_names = ",".join(flat_dict.keys())
            yield field_names + "\n"
        yield ",".join([str(item) for item in flat_dict.values()]) + "\n"
        flat_dict = {}


def txs_to_csv(json_data):
    flat_dict = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        else:
            flat_dict[name[:-1]] = x

    txs = json_data["txs"]
    block_height = json_data["height"]
    field_names = []
    for tx in txs:
        flat_dict["block_height"] = block_height
        flatten(tx)
        if not field_names:
            field_names = ",".join(flat_dict.keys())
            yield field_names + "\n"
        yield ",".join([str(item) for item in flat_dict.values()]) + "\n"
        flat_dict = {}


def flatten_rows(rows, field_names):
    flat_dict = dict()

    def flatten(item, name=""):
        if type(item) is dict:
            for sub_item in item:
                flatten(item[sub_item], name + sub_item + "_")
        else:
            flat_dict[name[:-1]] = item

    for row in rows:
        flatten(row)
        if not field_names:
            field_names = ",".join(flat_dict.keys())
            yield field_names + "\n"
        yield ",".join([str(item) for item in flat_dict.values()]) + "\n"
        flat_dict = dict()


def create_download_header(filename):
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename=filename)
    return headers
