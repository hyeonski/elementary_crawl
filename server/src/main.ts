import { NestFactory } from '@nestjs/core';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'path';
import { AppModule } from './app.module';
import * as hbs from 'hbs';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  app.useStaticAssets(join(__dirname, '..', 'public'));
  app.setBaseViewsDir(join(__dirname, '..', 'views'));

  hbs.registerHelper('isEqual', (lhs: any, rhs: any, options) =>
    lhs === rhs ? options.fn() : options.inverse(),
  );
  app.setViewEngine('hbs');

  await app.listen(3000);
}
bootstrap();
