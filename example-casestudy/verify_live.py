"""Integration checks against your configured MySQL database; no DDL or reset."""
import secrets
from dto import CustomerDTO, to_plain
from repositories import get_repository
from config import enabled


def main():
    modes = ['prepared', 'orm']
    if enabled('ALLOW_UNSAFE_SQL'):
        modes.insert(0, 'raw')
    else:
        print('Raw checks skipped; ALLOW_UNSAFE_SQL is false.')
    reference_orders = reference_details = None
    for mode in modes:
        repo = get_repository(mode)
        temporary_id = 'T' + secrets.token_hex(4)
        created = False
        try:
            # A unique temporary row leaves the existing teaching records intact.
            repo.create_customer(CustomerDTO(temporary_id, 'Test Customer'))
            created = True
            assert repo.get_customer(temporary_id).customer_name == 'Test Customer'
            repo.update_customer(temporary_id, 'Updated Customer')
            assert repo.get_customer(temporary_id).customer_name == 'Updated Customer'
            repo.delete_customer(temporary_id)
            created = False
            assert repo.get_customer(temporary_id) is None
            orders = to_plain(repo.customer_orders('C01'))
            details = to_plain(repo.order_details('O101'))
            if reference_orders is None:
                reference_orders, reference_details = orders, details
            assert orders == reference_orders and details == reference_details
            assert orders and details, 'Load the C01/O101 reference sample before this check.'
            if mode != 'raw':
                assert repo.search_customers("' OR '1'='1") == []
                # A valid apostrophe is stored as data by both safe implementations.
                repo.create_customer(CustomerDTO(temporary_id, "O'Connor"))
                created = True
                assert any(c.customer_id == temporary_id
                           for c in repo.search_customers("O'Connor"))
            else:
                assert len(repo.search_customers("' OR '1'='1")) == len(repo.list_customers())
            print(f'PASS {mode}: CRUD, 1-N, M-N and input handling')
        finally:
            if created:
                repo.delete_customer(temporary_id)
    print('All enabled modes passed. Temporary records removed.')


if __name__ == '__main__':
    main()
