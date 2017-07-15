import collections
import secrets


class ScopeTokenSet(frozenset):
    # language=rst
    """A frozenset that takes an iterable or a space delimited string and turns
    it into an immutable sequence of syntax-validated scope-tokens.

    Per :rfc:`6749#section-3.3`:

    .. code-block:: text

        The value of the scope parameter is expressed as a list of space-
        delimited, case-sensitive strings.  The strings are defined by the
        authorization server.  If the value contains multiple space-delimited
        strings, their order does not matter, and each string adds an
        additional access range to the requested scope.

            scope       = scope-token *( SP scope-token )
            scope-token = 1*( %x21 / %x23-5B / %x5D-7E )

    """

    allowed_charset = frozenset(
        chr(c) for c in (0x21, *range(0x23, 0x5B + 1), *range(0x5D, 0x7E + 1))
    )

    def __new__(cls, scope):
        scope_tokens = (isinstance(scope, str) and scope.split()) or scope
        try:
            if not all(set(s) <= cls.allowed_charset for s in scope_tokens):
                raise ValueError('scope-token can only contain {}'.format(
                    set(cls.allowed_charset)
                ))
        except TypeError:
            raise ValueError('ScopeTokenSet needs a str or iterable')
        return super().__new__(ScopeTokenSet, scope_tokens)


class AuthorizationCode(str):
    # language=rst
    """A wrapper around a urlsafe secret token of 160 bits / 20 bytes.

    From RFC6749, Section 10.10.  Credentials-Guessing Attacks:

    .. code-block:: text

        The probability of an attacker guessing generated tokens (and other
        credentials not intended for handling by end-users) MUST be less than
        or equal to 2^(-128) and SHOULD be less than or equal to 2^(-160).

    """
    def __new__(cls):
        return super().__new__(cls, secrets.token_urlsafe(nbytes=20))


Client = collections.namedtuple(
    'Client', 'identifier name secret redirect_uris owner_id idps'
)
"""The registration information for a client.

identifier (:rfc:`6749#section-2.2`):
    unique string. Using a uuid version 4 suffices,
    I think. URL safety would be nice. For example::

        >>> import base64
        >>> import uuid
        >>> base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]
        b'NOadtMwDSQKmw30l4l2xxQ'

secret / password (:rfc:`6749#section-2.3.1`):
    Only used by trusted clients. A random string with at least 128
    bits of entropy. Using base64 encoding, this requires 22 characters.

    We should use the secrets module for generating these. For example::

        >>> import base64
        >>> import secrets
        >>> base64.standard_b64encode(secrets.token_bytes(16))[:-2]
        b'XCAuw8B5u+EEBLALGOS9Aw'

redirect_uris (:rfc:`6749#section-3.1.2`):
    .. code-block:: text

        The redirection endpoint URI MUST be an absolute URI as
        defined by [RFC3986] Section 4.3.  The endpoint URI MAY
        include an "application/x-www-form-urlencoded" formatted (per
        Appendix B) query component ([RFC3986] Section 3.4), which
        MUST be retained when adding additional query parameters.
        The endpoint URI MUST NOT include a fragment component.


In addition to :rfc:`6749`, our implementation requires:

name
    the application name
owner_id
    user id of client owner. Note that this implies the owner must
    be a person. What this looks like depends on our user registration. For
    now, remains undecided.
idps
    a list of IdP identifiers. May be empty, in which case all
    authorization requests MUST specify an IdP.

"""
