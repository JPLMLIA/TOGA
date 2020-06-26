"""
Author: Shawn Anderson

Date  : 6/3/19

Brief :

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import asyncio
import os
import shutil

import aiohttp_cors
import yaml
from aiohttp import web

from toga.optimization_state.metrics import Metrics
from toga.optimization_state.paretofrontier import ParetoFrontier
from toga.server.frontier_state import FrontierState
from toga.toga_settings import Settings

class TogaServer(object):

    running_tests = False

    def __init__(self):
        self.settings = Settings()
        self.settings.create_output_directory()
        self.header = {'content-type': 'application/json'}

        # Storage for current run state of optimizer for front end
        self.pareto_frontier = ParetoFrontier(self.settings.output_dir, self.settings.optimization_strategy,
                                              Metrics(self.settings.optimization_metrics).metrics,
                                              self.settings.individual_per_bin,
                                              self.settings.history_log)
        # Update state from previous runs
        self.pareto_frontier.serialize()

        self.state = FrontierState(self.pareto_frontier)
        self.app = web.Application()

        self.loop = asyncio.get_event_loop()

        self.tasks = []

    def run(self):
        """

        :return:

        >>> from toga import _doctest
        >>> from toga.toga_settings import Settings
        >>> import signal
        >>> from multiprocessing import Process, Queue
        >>> import json
        >>> import subprocess
        >>> import concurrent.futures
        >>> settings = Settings()
        >>> server = TogaServer()
        >>> server.running_tests = True
        >>> server.run()
        running serialization
        launch webserver
        """
        if self.running_tests:
            self.loop.run_until_complete(self.schedule_serialization())
            print('launch webserver')
        else:
            self.tasks.append(self.loop.create_task(self.schedule_serialization()))
            self.start_web_server()
            try:
                self.loop.run_forever()
            except asyncio.CancelledError:
                self.stop()

    def stop(self):
        """

        :return:

        >>> server = TogaServer()
        >>> server.loop = asyncio.get_event_loop()
        >>> server.tasks.append(server.loop.create_task(server.schedule_serialization()))
        >>> server.stop()
        """
        for task in self.tasks:
            task.cancel()

    def serialize(self):
        """
        >>> from toga import _doctest
        >>> from toga.toga_settings import Settings
        >>> from toga.optimization_state.metrics import Metrics
        >>> from toga.optimization_state.paretofrontier import ParetoFrontier
        >>> import json
        >>> settings = Settings()
        >>> pareto_frontier = ParetoFrontier(settings.output_dir, settings.optimization_strategy,
        ...                                      Metrics(settings.optimization_metrics).metrics,
        ...                                      settings.individual_per_bin)
        >>> server = TogaServer()
        >>> server.pareto_frontier = pareto_frontier
        >>> server.state = FrontierState(server.pareto_frontier)
        >>> server.running_tests = True
        >>> state_path = os.path.join(_doctest.repo_abspath(), 'test', 'data', 'pareto_frontier_state', 'frontier.json')
        >>> with open(state_path) as f:
        ...     state = json.load(f)
        >>> server.state.pareto_frontier.update_from_local_datadict(state)
        >>> server.serialize()
        ['banana_0.033738250008640065_sinc_1.1813041113570979e-12_uuid_5590fa23433a4291878978e7a1a3c8f5.yml', 'banana_1.0826320258892002_sinc_6.271533083622613e-12_uuid_c9d2ec71a77b4a799ae376e8d9a6d0a9.yml', 'banana_8.987463785858072_sinc_1.1851181811392234e-11_uuid_6c8ad8cd4568498e8a701201e424d3ed.yml', 'banana_17.09732223439585_sinc_1.7505254015361264e-11_uuid_5499a2e44db24f84aae502239ca34e20.yml', 'banana_12.738008936955762_sinc_1.7651258507512963e-11_uuid_fbe102520d754fcc967510b675e46411.yml', 'banana_16.50089051508357_sinc_1.9306354168531728e-11_uuid_62bb5b875a83477f852c038e9fcbd1f5.yml', 'banana_30.252586348739325_sinc_-4.975575057803614e-11_uuid_04b66a840c164aa9a96a6f5debf69fdd.yml', 'banana_24.203878804187244_sinc_-4.5660086439018464e-11_uuid_402968e90ced47f3925b5644dda4634d.yml', 'banana_22.06089823367061_sinc_-4.2926648865496935e-11_uuid_227edb36e4914a61b5c26acc06b2bf83.yml', 'banana_33.437067668034885_sinc_-1.9816800183141552e-11_uuid_3f580ef5d1084f2aba32cae151657bb2.yml', 'banana_37.80657128205026_sinc_2.3719552233792703e-11_uuid_c838c50169fe41ae946cba6b8cb00458.yml', 'banana_37.748214202044146_sinc_2.456573590785539e-11_uuid_a7966fdcbc4e4afb8d29673360eb74cc.yml', 'banana_43.386152749015615_sinc_2.5357978518257443e-11_uuid_a808644ba80c4c7aa3a8c5887a716d57.yml', 'banana_46.78456321230448_sinc_2.576398164648546e-11_uuid_cf3f603334654c7eb918c7b88bdc349c.yml', 'banana_50.303498755471935_sinc_2.6136298682721094e-11_uuid_eef77f9456594d06aaef1d9c23244b0f.yml', 'banana_58.541753057059395_sinc_2.641750505226498e-11_uuid_26f3eacd55314f7ca830a441c9f25085.yml', 'banana_57.103586450183954_sinc_2.673790931518625e-11_uuid_29f524cabe6d4081959a9c20408b39c9.yml', 'banana_57.11865004898803_sinc_2.6739088698259573e-11_uuid_a00085013a00445b98810ca202fac702.yml', 'banana_63.87647234774193_sinc_-1.2548746919899206e-11_uuid_81ffd4ac388042049d1b5a57048abbe6.yml', 'banana_69.2808651352108_sinc_2.7211400350910646e-11_uuid_2b4e9f563b0244218cf2a0a71feaf9b8.yml', 'banana_70.18398015686277_sinc_2.7553639663839178e-11_uuid_00de2d089a2047b4a12e1bbf18978f60.yml', 'banana_78.96441601532686_sinc_-7.993135952046352e-12_uuid_b50a8fa8219a4a59aba4709b65d681c8.yml', 'banana_72.0384972914872_sinc_2.7640019889486628e-11_uuid_669aa9ec582e45f38ee027baff16e0bb.yml', 'banana_78.22027254248559_sinc_2.7884719647545804e-11_uuid_91b6598996b549b8aaf68db88614acb2.yml', 'banana_89.0410449669848_sinc_2.804682104452681e-11_uuid_fecd95db8c864d1582b8730b80e2afe4.yml', 'banana_89.94677204976904_sinc_2.8070456276200025e-11_uuid_bc2f15d7203f47dda01ca6b39f565dc9.yml', 'banana_90.15332849622976_sinc_2.8075695406353556e-11_uuid_46522c6d530d4af4b1cb90104f99b058.yml', 'banana_96.10410329289157_sinc_2.820378839861548e-11_uuid_627c61c16f204076b861979d28a7822d.yml', 'banana_98.52114784218405_sinc_2.8243981886163972e-11_uuid_64e130059b744592952018871677a758.yml', 'banana_99.20305975043196_sinc_2.8320124512552087e-11_uuid_5ceee04a02aa44cc8ae33d05208db2e8.yml', 'banana_108.83109864620499_sinc_-0.5_uuid_3075fa0fa5de4253878603209c6fe292.yml', 'banana_109.43103954247259_sinc_-0.5_uuid_6878652af6244274af6feffc812ab07b.yml', 'banana_111.65696156610596_sinc_2.8363107400027355e-11_uuid_3f8c352650934b50ba1704b220115b09.yml', 'banana_114.94450825289104_sinc_-0.5_uuid_c86a09a232e54c0fb82ce687d1750c38.yml', 'banana_116.35380110123123_sinc_4.135475261783844e-12_uuid_a204426c46fe4cb9b50321190ba19857.yml', 'banana_117.27096422667128_sinc_2.836329634326641e-11_uuid_ad46ad87d3564427b740e149be70da8a.yml', 'banana_130.19578611925078_sinc_-0.5_uuid_7105f53602484516a5e842b3e55353df.yml', 'banana_125.3284211488303_sinc_7.216559400341802e-12_uuid_3157d0443ce5473987e6701c5c58dd0c.yml', 'banana_132.50835669250515_sinc_2.818606740438852e-11_uuid_afa846da889149e4b46704b392ee85b1.yml', 'banana_142.2005248486548_sinc_-0.5_uuid_280815456d7e4263ac65260956f1b3da.yml', 'banana_141.82358367721355_sinc_2.8133240608899055e-11_uuid_2936d478b47a49c3b607e6471d127e15.yml', 'banana_141.08534633310404_sinc_2.8145033074401267e-11_uuid_be29b4dae5e34898afd3a5b8efcc7157.yml', 'banana_153.8365349351763_sinc_-0.5_uuid_3255a2c5c89343b181ec26a6ba50fc3f.yml', 'banana_144.32072900365716_sinc_2.798095129080619e-11_uuid_c07d83b9ffb544bc934b15107a73e43f.yml', 'banana_162.5_sinc_2.770842952113069e-11_uuid_e247f577a4544f62bc6f1a3caab720e5.yml', 'banana_155.7283913287429_sinc_2.7727306833435012e-11_uuid_50f04696a4984b15bb39f9d35e558d41.yml', 'banana_154.82791066261044_sinc_2.7885774321905598e-11_uuid_395dd61954cf47669194f849c383773d.yml', 'banana_172.45932399651264_sinc_-0.5_uuid_e9c637493a7649faba1dfba0c3820a64.yml', 'banana_164.7506168268209_sinc_2.1491495739343572e-11_uuid_79012e74f4154322a144aaad99ffa798.yml', 'banana_165.12459957097852_sinc_2.163256680628711e-11_uuid_e0b6bba697a941fca51f27e7f636aade.yml', 'banana_176.12988868967793_sinc_2.583049278946307e-11_uuid_e3c0016b747c462c9fdea7d7a9cb4aca.yml', 'banana_188.27558516272882_sinc_-0.5_uuid_cae613c2445f4750ba05fc4d87616f15.yml', 'banana_191.3933739571733_sinc_3.180052244296369e-11_uuid_fa584089e9fe44a4b05d861d80c6dae5.yml', 'banana_204.43357751882664_sinc_-0.5_uuid_b8f804da001c4bf7992c30d4023351db.yml', 'banana_196.53228040623875_sinc_3.38487880723903e-11_uuid_411bf53bcd864e8abfb685e1d355bacf.yml', 'banana_198.6635868010441_sinc_3.594315628321825e-11_uuid_31aa2af335ca4fddac94af935d77f9e1.yml', 'banana_214.89859241334136_sinc_-0.5_uuid_e4b582bac55e495585d6f8c4e2a601d9.yml', 'banana_212.11681954962305_sinc_-0.5_uuid_708f669bd181490b8090c10b7d251a46.yml', 'banana_207.00845298431494_sinc_-0.5_uuid_85d2c7e6a2df48ddb4ff50e56bea0b44.yml', 'banana_222.95104392053048_sinc_-0.5_uuid_e0640433ee644e989f0831620c6a6602.yml', 'banana_217.34081202575882_sinc_-0.5_uuid_08850f9a63684c36ac8dc24ac757e2d0.yml', 'banana_219.63586338506755_sinc_4.3292799193583845e-11_uuid_5776a325a24f47199d5d24e737c2bede.yml', 'banana_244.37580939662456_sinc_-0.5_uuid_177f5e6641eb4f82b323ef4c6404e9db.yml', 'banana_237.06612285139624_sinc_-0.5_uuid_a990105e3d7b4169a5e3714e3cd9ce28.yml', 'banana_245.95812042100962_sinc_5.4515931274066495e-11_uuid_4a6b008cdab045ecbaac9e11f2251501.yml', 'banana_248.71566793817703_sinc_-0.5_uuid_4c051ba4cd98499792c9c194434e76c0.yml', 'banana_246.45516501516448_sinc_5.587925929705804e-11_uuid_1c5237942a9a4d36ace20f57e647a07c.yml', 'banana_247.1671031725573_sinc_5.618813042954635e-11_uuid_b16c2c6e99054ea29b95c4c567a174c8.yml', 'banana_263.43390209880954_sinc_-0.5_uuid_5156497a7f2f483492a2d019294f32e6.yml', 'banana_262.46688783741473_sinc_-0.5_uuid_923cc0713fda49028f15d3da03d1fb25.yml', 'banana_273.4063888366453_sinc_-0.5_uuid_9a5ba456bbed49d3b71f594af57ff258.yml', 'banana_276.72508076028845_sinc_-0.5_uuid_6e506680c875426fbe1c74b3219e2516.yml', 'banana_270.21240632609147_sinc_-0.5_uuid_ffc90c0dd6fa4218bd1d2e71b3fe65f4.yml', 'banana_292.31240645997843_sinc_-0.5_uuid_4a73c8b01f3f43e0946fb865a07f5248.yml', 'banana_297.41104827267236_sinc_7.785495695710919e-11_uuid_b411c19249a54fafb0456d97952f00da.yml', 'banana_306.02238128209893_sinc_-0.5_uuid_6676d38b6b6c4079b9f212e951c69a7a.yml', 'banana_299.4616578186472_sinc_-0.5_uuid_0c9689be999d4b1e972217c26177dbe4.yml', 'banana_308.1989508582922_sinc_8.393093605411847e-11_uuid_5bd02e9147b346948a87d171aa43ca50.yml', 'banana_311.11239666426513_sinc_8.531688180090024e-11_uuid_bd4783c4a1c34c64b4db7cebf0a7ef9d.yml', 'banana_314.64633488882345_sinc_8.608309895118802e-11_uuid_f8c56236a90f472199a1a25775ceadc1.yml', 'banana_325.32872010521794_sinc_-0.5_uuid_6d77c9a448254dc4875f3b7e53fdfdba.yml', 'banana_328.68486832266564_sinc_9.29368524771754e-11_uuid_b3cc56f277fc469e9f4096748ba812b5.yml', 'banana_338.6403122174696_sinc_-0.5_uuid_baf5addfce114269b91342ee94b06bfc.yml', 'banana_340.54785457412464_sinc_-0.5_uuid_e677ae5b546c4cc5ae627844b002fa91.yml', 'banana_346.48284988500524_sinc_1.0182267759643485e-10_uuid_7654aa4dbc464464b1eecfadd67b53e3.yml', 'banana_348.72151542923035_sinc_1.0369830681592913e-10_uuid_e3f925015a3340bea03f912f9a14dbc7.yml', 'banana_351.43556840180435_sinc_1.0505943263737557e-10_uuid_a256226eb9654f3cbfb10d82b7ff19a2.yml', 'banana_358.42711841227685_sinc_1.0791055747601271e-10_uuid_a63a6f26a85c43979353d079f9ea48e8.yml', 'banana_367.29031830024314_sinc_-0.5_uuid_a96b2743e75e4c42a2cbe220c0a1beba.yml', 'banana_378.3784263602356_sinc_-0.5_uuid_cb5865403c8c4e118b999cd93cceedcb.yml', 'banana_374.75153674582015_sinc_1.169362838967863e-10_uuid_9d1ec92a50d742749ec5c756ab5362cc.yml', 'banana_376.08594012837443_sinc_1.1762555855706475e-10_uuid_c59ca950d5aa4dffbf05a842d7da0c5d.yml', 'banana_386.00991010396166_sinc_-0.5_uuid_3c8c26a7261a4a24b4fc862d24b3e3a7.yml', 'banana_393.2988361352649_sinc_1.262955335072594e-10_uuid_e1b1a2d6782644e296b29200754cd7e0.yml', 'banana_393.9593688410336_sinc_1.2693858995844534e-10_uuid_54a79c80a6a547dcbbaaee1c1106385c.yml', 'banana_398.7370633195467_sinc_1.2943469212058042e-10_uuid_2007b0809180404aab708d1a850bdc81.yml', 'banana_484.31297848651224_sinc_-0.5_uuid_cab64b2bc0fe459183ad93a04f6cc744.yml', 'banana_512.5_sinc_-0.5_uuid_9276d2d1c6b84c628129716d1432663d.yml', 'banana_400.79599206264487_sinc_1.3043590665423006e-10_uuid_1d1dbbba42fc4f0c9536083609bfa223.yml']
        """
        output_dir = self.settings.output_dir
        # Remove previous high performers
        best = os.path.join(output_dir, 'best')
        if os.path.exists(best):
            shutil.rmtree(best)
        if not os.path.exists(best):
            os.mkdir(best)

        # update this instance to match the the state handler
        self.pareto_frontier = self.state.pareto_frontier

        # Get high performing population
        population = self.pareto_frontier.datadict.serialize(self.settings.output_dir)
        paths = []

        # update the paths to save to and write them to file
        for individual in population:
            metrics = individual.get('metrics')
            if metrics is not None:
                out = ''
                for key, item in metrics.items():
                    assert not isinstance(item, dict)
                    out += f'{key}_{item}_'
                uuid = individual.get('uuid')
                out_path = os.path.join(output_dir, 'best', f'{out}uuid_{uuid}.yml')
                if self.running_tests:
                    paths.append(out_path)
                if not self.running_tests:
                    with open(out_path, 'w') as f:
                        yaml.dump(individual, f)

        # plot state
        if not self.running_tests and population is not None and len(population) > 0:
            self.pareto_frontier.plot()

        # For testing
        if self.running_tests:
            basenames = [os.path.basename(p) for p in paths]
            print(basenames)

    async def schedule_serialization(self):
        """

        :return:

        >>> server = TogaServer()
        >>> server.running_tests = True
        >>> server.loop.run_until_complete(server.schedule_serialization())
        running serialization
        """
        if self.running_tests:
            print('running serialization')
        else:
            while True:
                self.serialize()
                print('running serialization')
                await asyncio.sleep(600)

    def start_web_server(self) -> None:
        """

        :return:

        >>> server = TogaServer()
        >>> server.running_tests = True
        >>> server.start_web_server()
        >>> server.app.router.routes().__dict__.values()
        dict_values([[<ResourceRoute [PUT] <PlainResource  /submit> -> <bound method FrontierState.submit_individual of <toga.server.frontier_state.FrontierState object at 0x...>>, <ResourceRoute [OPTIONS] <PlainResource  /submit> -> <bound method _PreflightHandler._preflight_handler of <aiohttp_cors.cors_config._CorsConfigImpl object at 0x...>>, <ResourceRoute [GET] <PlainResource  /get_state> -> <bound method FrontierState.get_state of <toga.server.frontier_state.FrontierState object at 0x...>>, <ResourceRoute [OPTIONS] <PlainResource  /get_state> -> <bound method _PreflightHandler._preflight_handler of <aiohttp_cors.cors_config._CorsConfigImpl object at 0x...>>]])
        """

        self.app.router.add_route('PUT', '/submit', self.state.submit_individual)
        self.app.router.add_route('GET', '/get_state', self.state.get_state)

        # Configure default CORS settings.
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Configure CORS on all routes.
        for route in list(self.app.router.routes()):
            cors.add(route)

        if not self.running_tests:
            print('running server')
            web.run_app(self.app, host=self.settings.host, port=self.settings.port,  access_log=None)


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    # TogaServer().run()
