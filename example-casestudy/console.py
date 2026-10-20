"""Run this file from VS Code's terminal. All database work stays in repositories."""
import argparse
import json
import sys
from mysql.connector import Error as MySQLError
from sqlalchemy.exc import SQLAlchemyError
from dto import CustomerDTO, to_plain
from repositories import MODES, get_repository


def show(value):
    print(json.dumps(to_plain(value), indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description='Restaurant console: reuse the same code as Flask.')
    parser.add_argument('--mode', choices=MODES, default='prepared')
    parser.add_argument('action', choices=(
        'list', 'get', 'create', 'update', 'delete', 'search', 'orders', 'details',
        'crud-demo', 'injection-demo',
    ))
    parser.add_argument('--id', help='CustomerID for customer operations; OrderID for details.')
    parser.add_argument('--name', help='Customer name for create, update or exact search.')
    args = parser.parse_args()
    try:
        repo = get_repository(args.mode)
        action = args.action
        if action in {'get', 'create', 'update', 'delete', 'orders', 'details'} and not args.id:
            parser.error('--id is required for this action.')
        if action in {'create', 'update', 'search'} and args.name is None:
            parser.error('--name is required for this action.')
        if action in {'create', 'update'} and (
            not args.name.strip() or len(args.name) > 100 or len(args.id) > 10
        ):
            parser.error('Use a nonblank name of at most 100 characters and an ID of at most 10.')
        if action == 'list':
            show(repo.list_customers())
        elif action == 'get':
            show(repo.get_customer(args.id))
        elif action == 'create':
            show(repo.create_customer(CustomerDTO(args.id, args.name)))
        elif action == 'update':
            count = repo.update_customer(args.id, args.name)
            show({'affected_or_matched': count, 'customer': repo.get_customer(args.id)})
        elif action == 'delete':
            show({'deleted': repo.delete_customer(args.id)})
        elif action == 'search':
            show(repo.search_customers(args.name))
        elif action == 'orders':
            show(repo.customer_orders(args.id))
        elif action == 'details':
            show(repo.order_details(args.id))
        elif action == 'crud-demo':
            # Refuse to overwrite somebody else's CTEST. Each method commits separately.
            if repo.get_customer('CTEST') is not None:
                raise ValueError('CTEST already exists. Choose another ID with individual commands.')
            show({'create': repo.create_customer(CustomerDTO('CTEST', 'Dewi'))})
            show({'read': repo.get_customer('CTEST')})
            repo.update_customer('CTEST', 'Dewi Putri')
            show({'update': repo.get_customer('CTEST')})
            show({'delete': repo.delete_customer('CTEST')})
            show({'after_delete': repo.get_customer('CTEST')})
        elif action == 'injection-demo':
            # SELECT only: no destructive payload is needed to explain injection.
            for name in ('Made', "' OR '1'='1", "O'Connor"):
                print('Search value:', repr(name))
                try:
                    show(repo.search_customers(name))
                except (MySQLError, SQLAlchemyError) as error:
                    print('Query failed:', type(error).__name__)
                    print('An interpolated apostrophe can change or break SQL syntax.')
        return 0
    except (ValueError, MySQLError, SQLAlchemyError) as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
