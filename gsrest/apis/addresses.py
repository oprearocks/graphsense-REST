from flask import Response
from flask_restplus import Namespace, Resource

from gsrest.apis.common import page_size_parser, neighbors_parser, \
    address_txs_response, address_tags_response, entity_tags_response, \
    tag_response, neighbors_response
import gsrest.service.addresses_service as addressesDAO
import gsrest.service.common_service as commonDAO
import gsrest.service.entities_service as entitiesDAO
from gsrest.util.csvify import tags_to_csv, create_download_header, \
    flatten_rows
from gsrest.util.checks import check_inputs
from gsrest.util.decorator import token_required

api = Namespace('addresses',
                path='/<currency>/addresses',
                description='Operations related to addresses')


@api.route("/<address>")
@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
class Address(Resource):
    @token_required
    @api.marshal_with(address_tags_response)
    def get(self, currency, address):
        """
        Returns details and optionally tags of a specific address
        """
        check_inputs(address=address, currency=currency)  # abort if fails
        addr = commonDAO.get_address(currency, address)  # abort if not found
        addr['tags'] = commonDAO.list_address_tags(currency, address)
        return addr


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/txs")
class AddressTxs(Resource):
    @token_required
    @api.doc(parser=page_size_parser)
    @api.marshal_with(address_txs_response)
    def get(self, currency, address):
        """
        Returns all transactions an address has been involved in
        """
        args = page_size_parser.parse_args()
        page = args['page']
        pagesize = args['pagesize']
        check_inputs(address=address, currency=currency, page=page,
                     pagesize=pagesize)  # abort if fails
        paging_state = bytes.fromhex(page) if page else None
        # abort if not found
        paging_state, address_txs = addressesDAO.list_address_txs(currency,
                                                                  address,
                                                                  paging_state,
                                                                  pagesize)
        return {"next_page": paging_state.hex() if paging_state else None,
                "address_txs": address_txs}


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/tags")
class AddressTags(Resource):
    @token_required
    @api.marshal_list_with(tag_response)
    def get(self, currency, address):
        """
        Returns attribution tags for a given address
        """
        check_inputs(address=address, currency=currency)  # abort if fails
        address_tags = commonDAO.list_address_tags(currency, address)
        return address_tags  # can be empty list


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/tags.csv")
class AddressTagsCSV(Resource):
    @token_required
    def get(self, currency, address):
        """
        Returns attribution tags for a given address as CSV
        """
        check_inputs(address=address, currency=currency)  # abort if fails
        tags = commonDAO.list_address_tags(currency, address)
        return Response(tags_to_csv(tags), mimetype="text/csv",
                        headers=create_download_header('tags of address {} '
                                                       '({}).csv'
                                                       .format(address,
                                                               currency
                                                               .upper())))


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/neighbors")
class AddressNeighbors(Resource):
    @token_required
    @api.doc(parser=neighbors_parser)
    @api.marshal_with(neighbors_response)
    def get(self, currency, address):
        """
        Returns an addresses' neighbors in the address graph
        """
        args = neighbors_parser.parse_args()
        direction = args.get("direction")
        page = args.get("page")
        pagesize = args.get("pagesize")
        check_inputs(address=address, currency=currency, direction=direction,
                     page=page, pagesize=pagesize)
        paging_state = bytes.fromhex(page) if page else None
        if "in" in direction:
            paging_state, relations = addressesDAO\
                .list_address_incoming_relations(currency, address,
                                                 paging_state, pagesize)
        else:
            paging_state, relations = addressesDAO\
                .list_address_outgoing_relations(currency, address,
                                                 paging_state, pagesize)
        return {"next_page": paging_state.hex() if paging_state else None,
                "neighbors": relations}


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/neighbors.csv")
class AddressNeighborsCSV(Resource):
    @token_required
    @api.doc(parser=neighbors_parser)
    def get(self, currency, address):
        """
        Returns addresses' neighbors in the address graph as CSV
        """
        args = neighbors_parser.parse_args()
        direction = args.get("direction")
        page = args.get("page")
        pagesize = args.get("pagesize")
        paging_state = bytes.fromhex(page) if page else None
        check_inputs(address=address, currency=currency, direction=direction,
                     page=page, pagesize=pagesize)
        if "in" in direction:
            query_function = addressesDAO.list_address_incoming_relations
        else:
            query_function = addressesDAO.list_address_outgoing_relations
        columns = []
        data = ''
        while True:
            paging_state, neighbors = query_function(currency, address,
                                                     paging_state, pagesize)
            for row in flatten_rows(neighbors, columns):
                data += row
            if not paging_state:
                break
        return Response(data,
                        mimetype="text/csv",
                        headers=create_download_header(
                            'neighbors of address {} ({}).csv'
                            .format(address, currency.upper())))


@api.param('currency', 'The cryptocurrency (e.g., btc)')
@api.param('address', 'The cryptocurrency address')
@api.route("/<address>/entity")
class AddressEntity(Resource):
    @token_required
    @api.marshal_with(entity_tags_response)
    def get(self, currency, address):
        """
        Returns the associated entity for a given address
        """
        check_inputs(address=address, currency=currency)  # abort if fails
        # abort if not found
        entity = addressesDAO.get_address_entity(currency, address)
        entity['tags'] = entitiesDAO.list_entity_tags(currency,
                                                      entity['entity'])
        return entity
