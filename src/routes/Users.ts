import StatusCodes from 'http-status-codes';
import { Request, Response } from 'express';

import UserDao from '@daos/User/UserDao';
import { paramMissingError } from '@shared/constants';
import logger from '@shared/Logger';

const userDao = new UserDao();
const { BAD_REQUEST, OK } = StatusCodes;


/**
 * Add one user.
 * 
 * @param req 
 * @param res 
 * @returns 
 */
export async function notifyUser(req: Request, res: Response) {
    try {
        const { message } = req.body;
        if (!message) {
            logger.err(paramMissingError);
            return res.status(BAD_REQUEST).json({
                error: paramMissingError,
            });
        }
        logger.info(`Notifying user with message: ${message}`);
        await userDao.notify(message);
        return res.status(OK).json({message: 'Notification sent'}).end();
    } catch (error) {
        logger.err(error);
        res.status(BAD_REQUEST).json({
            error: error,
        });
    }
}
