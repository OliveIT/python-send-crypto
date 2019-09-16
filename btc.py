from bit import PrivateKey
import blockcypher

APIKEY='...'

def sendBTC (fromAddress, toAddress, satValue, satFee, fromWIF ):
    """Send Bitcoin from `fromAddress` to `toAddress`.

    Args:
        fromAddress (str): Address of sender.
        toAddress (str): Address of recipient.
        satValue (int): Transaction amount in Satoshi.
            Pass -1 to send entire balance.
        satFee (int): Transaction fee in Satoshi.
        fromWIF (str): WIF string of sender.

    Returns:
        Success:
            {
                'status': 'success',
                'result': decoded transaction
            }
        Failure:
            {
                'status': 'failure',
                'error': error message
            }
    """
    response = {
        'status': 'failure',
    }
    try:
        # validation
        if len(fromAddress) != 34:
            response['error'] = "fromAddress should be 34 letters."
            return response
        if len(toAddress) != 34:
            response['error'] = "toAddress should be 34 letters."
            return response
        if len(fromWIF) != 52:
            response['error'] = "fromWIF should be 52 letters."
            return response

        key = PrivateKey(wif=fromWIF)
        if key.address != fromAddress:
            response['error'] = "fromAddress can't be derived from fromWIF."
            return response

        key.get_balance(currency='satoshi')
        satBalance = key.balance

        if satValue == -1: # sending all amount
            if satBalance < satFee:
                response['error'] = "insufficient balance. less than tx fee."
                return response
        else:
            if satBalance < satFee + satValue:
                response['error'] = "insufficient balance."
                return response

        # create transaction
        key.get_transactions()
        key.get_unspents()

        if satValue == -1: # sending all amount
            rawtx = key.create_transaction(outputs=[], leftover=toAddress, fee=satFee, absolute_fee=True)
        else:
            output1 = (toAddress, satValue, 'satoshi')
            output2 = (fromAddress, satBalance - satValue - satFee, 'satoshi')
            rawtx = key.create_transaction(outputs=[output1, output2], fee=satFee, absolute_fee=True)

        # push transaction
        decodedTx = blockcypher.pushtx(tx_hex=rawtx, coin_symbol='btc', api_key=APIKEY)

        response['status'] = 'success'
        response['result'] = decodedTx

        return response
    except TypeError as err:
        response['error'] = str(err)
        return response
    except Exception as err:
        response['error'] = str(err)
        return response
    response['error'] = 'unexpected error occured.'
    return response
