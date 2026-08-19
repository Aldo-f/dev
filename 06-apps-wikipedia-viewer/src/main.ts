import './polyfills';

import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule).then(ref => {
  // Ensure Angular destroys itself on hot reloads.
  const win: any = window;
  if (win['ngRef']) {
    win['ngRef'].destroy();
  }
  win['ngRef'] = ref;

  // Otherwise, log the boot error
}).catch(err => console.error(err));