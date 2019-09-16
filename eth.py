import requests
from web3 import Web3, HTTPProvider

APIKEY='...'
INFURAKEY='...'

w3 = Web3(HTTPProvider('https://mainnet.infura.io/' + INFURAKEY))

def sendETH (fromAddress, toAddress, weiValue, weiGasPrice, fromWIF ):
    """Send testnet Ether from `fromAddress` to `toAddress`.

    Args:
        fromAddress (str): Address of sender.
        toAddress (str): Address of recipient.
        weiValue (int): Transaction amount in Wei.
            Pass -1 to send entire balance.
        weiGasPrice (int): Gas price in Wei.
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
        if len(fromAddress) != 42:
            response['error'] = "fromAddress should be 34 letters."
            return response
        if len(toAddress) != 42:
            response['error'] = "toAddress should be 34 letters."
            return response
        if len(fromWIF) != 64:
            response['error'] = "fromWIF should be 52 letters."
            return response

        account = w3.eth.account.from_key(fromWIF);

        if account.address != fromAddress:
            response['error'] = "fromAddress cannot be derived from fromWIF."
            return response

        weiBalance = w3.eth.getBalance(fromAddress)

        # build transaction

        txInfo = {
            'nonce': w3.eth.getTransactionCount(fromAddress),
            'gasPrice': weiGasPrice, # w3.eth.gasPrice
            'gas': 21000,
            'to': toAddress,
            'value': 0
        }

        weiFee = txInfo['gasPrice'] * txInfo['gas']

        if weiValue == -1: # sending all amount
            if weiBalance < weiFee:
                response['error'] = "insufficient balance. less than tx fee."
                return response
            else:
                txInfo['value'] = weiBalance - weiFee
        else:
            if weiBalance < weiFee + weiValue:
                response['error'] = "insufficient balance."
                return response
            else:
                txInfo['value'] = weiValue

        signedTx = w3.eth.account.sign_transaction(txInfo, fromWIF)

        # push transaction

        result = requests.post(
            url='https://api.blockcypher.com/v1/eth/main/txs/push',
            params={'token' : APIKEY},
            json={ 'tx': (signedTx.rawTransaction.hex())[2:] }
        )

        result.raise_for_status()

        response['status'] = 'success'
        response['result'] = result.json()
        return response
    except TypeError as err:
        response['error'] = str(err)
        return response
    except Exception as err:
        response['error'] = str(err)
        return response
    response['error'] = 'unexpected error occured.'
    return response
