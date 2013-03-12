from mysubtree.web.user import get_user_node

def refresh_account(route):
    def wrapper(**kwargs):
        old_user = get_user_node()
        response = route(**kwargs)
        is_refresh_needed = get_user_node() != old_user
        if isinstance(response, dict):
            if is_refresh_needed:
                return {
                    "refresh_account": response
                }
            else:
                return response
        return response # HTML
    wrapper.__name__ = route.__name__ # for url_for to work
    return wrapper
