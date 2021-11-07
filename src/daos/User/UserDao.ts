import { IUser } from '@entities/User';
import logger from '@shared/Logger';
import { tokenTelegram, chatId } from '@shared/constants';
import Telegram from '@services/telegramBot';

export interface IUserDao {
    notify: (message: string) => Promise<unknown>;
}

class UserDao implements IUserDao {
    private telegram: Telegram;
    constructor() {
       this.telegram = new Telegram(tokenTelegram, chatId);
    }

    /**
     *
     * @param message
     */
    public async notify(message: string): Promise<unknown> {
        logger.info(`UserDao.notify: ${message}`);
        return this.telegram.sendMessage(message);
    }


}

export default UserDao;
