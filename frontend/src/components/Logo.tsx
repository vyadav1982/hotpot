import React from 'react';

interface LogoAttributes {
  className?: string;
}

export const Logo: React.FC<LogoAttributes> = ({
  className = '',
}: LogoAttributes) => {
  return (
    <svg
      version="1.1"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`0 0 512 512`}
    >
      <path
        d="M0 0 C1.29885251 -0.00128164 1.29885251 -0.00128164 2.62394446 -0.00258917 C5.52435705 -0.0042358 8.42471176 0.00126407 11.32511902 0.00672913 C13.40464781 0.0070112 15.48417671 0.00685287 17.56370544 0.00628662 C23.20993221 0.00599943 28.85613779 0.0118835 34.50235963 0.01886058 C40.40272556 0.02510717 46.30309197 0.02569895 52.20346069 0.02688599 C63.37703655 0.02999544 74.55060264 0.03820366 85.7241742 0.04823548 C98.44472397 0.05940856 111.16527421 0.06491008 123.88582766 0.06993091 C150.05334101 0.08038657 176.22084568 0.09797858 202.38835144 0.12025452 C202.44893738 1.15666077 202.50952332 2.19306702 202.57194519 3.26087952 C202.65638515 4.63068325 202.74103141 6.00047427 202.82585144 7.37025452 C202.86516785 8.05216858 202.90448425 8.73408264 202.94499207 9.43666077 C203.15501616 12.76473493 203.40769146 15.92280853 204.38835144 19.12025452 C208.49058729 20.13565564 208.49058729 20.13565564 212.38835144 19.12025452 C213.78304259 15.38876296 213.72361988 11.31141823 213.95085144 7.37025452 C214.01562683 6.3241803 214.01562683 6.3241803 214.08171082 5.25697327 C214.1872474 3.54493529 214.28825054 1.83261891 214.38835144 0.12025452 C241.72660854 0.05013833 269.06485214 -0.0027465 296.40318108 -0.035182 C309.09716169 -0.05064341 321.7910864 -0.07171915 334.48503113 -0.10606384 C345.55052545 -0.1359883 356.61597929 -0.15532576 367.68151295 -0.16201097 C373.53929669 -0.16591803 379.39696458 -0.17508527 385.25471115 -0.19693565 C390.77204046 -0.21734882 396.28920657 -0.22356947 401.80657005 -0.21906853 C403.82775065 -0.21989156 405.8489369 -0.22582829 407.87008476 -0.23736191 C421.57355478 -0.31170247 433.42950446 -0.18006965 444.38835144 9.12025452 C451.46154686 16.57954139 453.84724822 24.53177975 453.77603149 34.59483337 C453.7841098 35.97882724 453.7841098 35.97882724 453.79235131 37.39078057 C453.80659755 40.46594484 453.79953531 43.54067663 453.79240417 46.61585999 C453.7981095 48.827391 453.80507439 51.03891907 453.8132019 53.2504425 C453.83113103 59.24635929 453.82996526 65.24212971 453.82425952 71.23806524 C453.82116713 76.24795652 453.82726074 81.25781971 453.83329827 86.26770699 C453.8481437 98.76467353 453.84453072 111.2615695 453.83243496 123.75853099 C453.82250564 134.59569732 453.83544022 145.43269284 453.85936915 156.26983283 C453.88379012 167.41432712 453.89296137 178.55875958 453.88671643 189.70328438 C453.88334851 195.95330904 453.88575104 202.20319261 453.90296745 208.45319748 C453.91845438 214.33184396 453.91446127 220.21016483 453.89566231 226.08879852 C453.89198122 228.24220595 453.89507081 230.39563759 453.9055481 232.54902267 C453.91879252 235.49695717 453.90717959 238.44381916 453.88955688 241.39170837 C453.89916189 242.23647732 453.9087669 243.08124626 453.91866297 243.95161426 C453.80977286 252.8523378 450.69547616 260.7741236 444.58366394 267.29603577 C436.19987197 274.26263871 427.37529668 276.27879156 416.77670288 276.24050903 C415.91080121 276.24136346 415.04489954 276.24221788 414.15275842 276.2430982 C411.25234583 276.24474484 408.35199112 276.23924496 405.45158386 276.23377991 C403.37205507 276.23349783 401.29252617 276.23365616 399.21299744 276.23422241 C393.56677067 276.2345096 387.92056509 276.22862553 382.27434325 276.22164845 C376.37397732 276.21540187 370.47361092 276.21481008 364.57324219 276.21362305 C353.39966633 276.21051359 342.22610024 276.20230538 331.05252868 276.19227356 C318.33197891 276.18110047 305.61142868 276.17559895 292.89087522 276.17057812 C266.72336187 276.16012246 240.5558572 276.14253046 214.38835144 276.12025452 C214.3277655 275.08384827 214.26717957 274.04744202 214.20475769 272.97962952 C214.12031773 271.60982579 214.03567147 270.24003476 213.95085144 268.87025452 C213.91153503 268.18834045 213.87221863 267.50642639 213.83171082 266.80384827 C213.62168672 263.47577411 213.36901142 260.3177005 212.38835144 257.12025452 C208.28611559 256.10485339 208.28611559 256.10485339 204.38835144 257.12025452 C202.99366029 260.85174607 203.053083 264.9290908 202.82585144 268.87025452 C202.76107605 269.91632874 202.76107605 269.91632874 202.69499207 270.98353577 C202.58945548 272.69557374 202.48845234 274.40789013 202.38835144 276.12025452 C175.05009434 276.1903707 147.71185075 276.24325553 120.3735218 276.27569103 C107.67954119 276.29115245 94.98561648 276.31222819 82.29167175 276.34657288 C71.22617743 276.37649733 60.1607236 276.39583479 49.09518993 276.40252 C43.23740619 276.40642707 37.3797383 276.41559431 31.52199173 276.43744469 C26.00466242 276.45785786 20.48749631 276.46407851 14.97013283 276.45957756 C12.94895223 276.4604006 10.92776598 276.46633732 8.90661812 276.47787094 C-4.7968519 276.5522115 -16.65280158 276.42057868 -27.61164856 267.12025452 C-34.68484398 259.66096764 -37.07054534 251.70872929 -36.99932861 241.64567566 C-37.00740692 240.2616818 -37.00740692 240.2616818 -37.01564842 238.84972847 C-37.02989467 235.77456419 -37.02283243 232.6998324 -37.01570129 229.62464905 C-37.02140662 227.41311803 -37.0283715 225.20158997 -37.03649902 222.99006653 C-37.05442814 216.99414974 -37.05326238 210.99837932 -37.04755664 205.00244379 C-37.04446425 199.99255251 -37.05055786 194.98268932 -37.05659539 189.97280204 C-37.07144082 177.4758355 -37.06782784 164.97893954 -37.05573208 152.48197804 C-37.04580276 141.64481171 -37.05873734 130.80781619 -37.08266627 119.9706762 C-37.10708724 108.82618191 -37.11625849 97.68174946 -37.11001354 86.53722465 C-37.10664563 80.28719999 -37.10904816 74.03731642 -37.12626457 67.78731155 C-37.1417515 61.90866508 -37.13775839 56.03034421 -37.11895943 50.15171051 C-37.11527834 47.99830308 -37.11836792 45.84487144 -37.12884521 43.69148636 C-37.14208964 40.74355187 -37.1304767 37.79668988 -37.112854 34.84880066 C-37.12245901 34.00403172 -37.13206402 33.15926277 -37.14196008 32.28889477 C-37.03306998 23.38817124 -33.91877327 15.46638544 -27.80696106 8.94447327 C-19.42316908 1.97787033 -10.5985938 -0.03828253 0 0 Z M203.38835144 40.12025452 C201.63355083 45.38465635 202.1612616 50.98536122 202.13835144 56.49525452 C202.11772644 57.72759827 202.09710144 58.95994202 202.07585144 60.22962952 C202.07069519 61.41814514 202.06553894 62.60666077 202.06022644 63.83119202 C202.05088074 64.91706604 202.04153503 66.00294006 202.03190613 67.12171936 C202.43557331 70.51750044 203.37046769 72.38521563 205.38835144 75.12025452 C207.26792388 76.27791302 207.26792388 76.27791302 209.38835144 76.12025452 C212.46376626 74.36287462 213.24817142 73.54079458 214.38835144 70.12025452 C214.6503118 65.66613453 214.61980263 61.20624382 214.63835144 56.74525452 C214.65897644 55.51291077 214.67960144 54.28056702 214.70085144 53.01087952 C214.70858582 51.22810608 214.70858582 51.22810608 214.71647644 49.40931702 C214.72582214 48.32344299 214.73516785 47.23756897 214.74479675 46.11878967 C214.34112957 42.72300859 213.40623519 40.85529341 211.38835144 38.12025452 C207.82216498 36.27964215 206.13856136 37.46487942 203.38835144 40.12025452 Z M2.38835144 61.12025452 C-2.88209793 67.64496948 -6.3678486 76.37284542 -5.95539856 84.86244202 C-4.35909157 95.34727657 -0.74615992 104.10010583 7.56022644 110.89759827 C9.77682603 112.46068315 12.00912308 113.8202208 14.38835144 115.12025452 C14.99034363 115.46056702 15.59233582 115.80087952 16.21257019 116.15150452 C23.44809118 119.54168355 32.67702487 119.23958982 40.29850769 117.42884827 C50.2752869 113.74345378 57.27910987 107.42203996 62.38835144 98.12025452 C66.20699919 89.27568893 66.4623931 79.99908985 63.25553894 70.90931702 C57.97305193 59.44949547 50.64930086 53.23759392 39.07585144 48.87025452 C24.38300392 45.88187875 12.40427225 50.01804818 2.38835144 61.12025452 Z M126.59416199 74.39686584 C125.31790285 75.66769939 124.04079552 76.93768161 122.76290894 78.20687866 C119.307627 81.64397851 115.86505374 85.09354662 112.42521262 88.54609132 C108.81848397 92.16297185 105.2019777 95.77005468 101.58703613 99.37872314 C95.52002329 105.43846692 89.46147477 111.50657746 83.40763855 117.57948303 C76.41342646 124.59547211 69.40490785 131.59692189 62.38880318 138.59101278 C56.35833073 144.60332197 50.33570252 150.62340541 44.31953841 156.65003222 C40.72930794 160.2464912 37.13644758 163.84021091 33.53648949 167.4269352 C30.15306075 170.7987924 26.77959924 174.18031713 23.41351509 177.56948662 C22.17819597 178.81008534 20.93947769 180.04731022 19.69710541 181.28084564 C17.99882548 182.96815776 16.31340254 184.66737285 14.63058472 186.37008667 C14.13895692 186.85279158 13.64732912 187.33549649 13.14080352 187.83282882 C9.28463293 191.77762103 6.8154257 195.95886335 6.06803894 201.49134827 C6.68319099 207.99965694 9.43277789 211.9223513 14.38835144 216.12025452 C18.46585182 218.2891377 21.79623265 218.26526689 26.26335144 217.79994202 C31.78099666 216.03510697 35.95456107 211.84525478 39.94906616 207.81350708 C40.73762299 207.02963022 40.73762299 207.02963022 41.54211026 206.22991747 C43.29014002 204.48982053 45.03098623 202.7427163 46.77189636 200.99549866 C48.02856798 199.74153896 49.28566428 198.48800472 50.54315186 197.23486328 C53.94840298 193.83871352 57.34731695 190.43628743 60.7448442 187.03241277 C64.30386904 183.46831741 67.86777897 179.90911227 71.4309082 176.34912109 C77.4121062 170.37155919 83.38908043 164.38979824 89.36369324 158.40565491 C96.26959264 151.48886669 103.18267416 144.57931958 110.09952086 137.67348009 C116.04133113 131.74074689 121.97923358 125.80412361 127.91388971 119.86423391 C131.4570191 116.31798778 135.00148285 112.77310374 138.54947472 109.23172188 C141.88398611 105.90298955 145.21356351 102.56939927 148.53940392 99.23200417 C149.76033667 98.00842806 150.98297245 96.78654858 152.20743179 95.56650162 C153.87915496 93.90024789 155.54458909 92.22794846 157.20858765 90.5539856 C157.93640286 89.83286255 157.93640286 89.83286255 158.6789214 89.09717137 C163.4964068 84.22362058 166.15243451 80.07980399 166.38835144 73.12025452 C165.37759157 67.57182801 162.86689519 63.68337235 158.40788269 60.25697327 C145.30566526 52.88222419 135.06063421 65.86963231 126.59416199 74.39686584 Z M315.57585144 75.09681702 C312.67053603 80.04732156 311.20775331 85.02531616 311.70085144 90.74525452 C311.92772644 91.52900452 312.15460144 92.31275452 312.38835144 93.12025452 C311.49309753 93.28847717 311.49309753 93.28847717 310.57975769 93.46009827 C289.18325226 98.32438553 270.79590976 113.21902876 259.20085144 131.49525452 C250.90665699 145.50286666 245.11843636 160.52968846 245.32585144 176.99525452 C245.33036316 177.68361389 245.33487488 178.37197327 245.33952332 179.08119202 C245.35118808 180.76091787 245.36911874 182.44059827 245.38835144 184.12025452 C244.15085144 184.34712952 242.91335144 184.57400452 241.63835144 184.80775452 C238.54479789 185.59759798 237.37179226 186.1347438 234.88835144 188.30775452 C232.93644429 191.96758043 232.74111841 194.02111198 233.38835144 198.12025452 C235.18730818 201.08753741 237.23536001 203.5437588 240.38835144 205.12025452 C242.8684073 205.2265548 245.32092094 205.2724617 247.80162048 205.27415466 C248.57497089 205.27853692 249.34832129 205.28291917 250.14510655 205.28743422 C252.75060465 205.30084685 255.3560689 205.3070066 257.96159363 205.31312561 C259.82405247 205.32102464 261.68650977 205.32929346 263.54896545 205.33790588 C269.6777042 205.3641491 275.80644986 205.37943584 281.93522644 205.39369202 C284.04316971 205.39905076 286.15111292 205.40442826 288.25905609 205.40982437 C297.02620221 205.43145649 305.79334648 205.45019396 314.56051254 205.46144676 C327.13438691 205.47769038 339.70795246 205.51087451 352.28171039 205.56784761 C361.11744023 205.60652127 369.95308739 205.62607641 378.78889966 205.63136733 C384.06869875 205.63502432 389.34816865 205.64708255 394.62787628 205.67947006 C399.5954094 205.70950527 404.56241335 205.71587873 409.53001785 205.7040863 C411.35293422 205.70386519 413.17587481 205.71220165 414.99870682 205.72974014 C417.48882561 205.75239411 419.97701944 205.74415571 422.46714783 205.72825623 C423.18758672 205.74213831 423.9080256 205.7560204 424.65029597 205.77032316 C430.27952581 205.68183728 432.57402896 203.96365898 436.38835144 200.12025452 C437.93859608 197.01976523 437.67827159 194.54131234 437.38835144 191.12025452 C435.78866367 188.12083995 434.57330503 186.55443598 431.34147644 185.37025452 C429.37685266 184.86864844 427.38275903 184.48589591 425.38835144 184.12025452 C425.42315613 183.19986389 425.45796082 182.27947327 425.49382019 181.33119202 C426.00329656 157.50710659 417.07631603 135.93568768 401.38835144 118.12025452 C389.82080728 106.13480775 374.92717829 96.36316174 358.38835144 93.12025452 C358.61522644 92.33650452 358.84210144 91.55275452 359.07585144 90.74525452 C359.66618166 83.89742393 357.5497309 78.08827635 353.26335144 72.74525452 C348.23171659 67.53429516 342.68086742 64.99971474 335.45085144 64.55775452 C327.5020662 64.92861541 320.41326983 68.80267605 315.57585144 75.09681702 Z M203.38835144 94.12025452 C201.38891073 99.32357472 202.16221328 105.57847863 202.13835144 111.05775452 C202.11772644 112.23789124 202.09710144 113.41802795 202.07585144 114.63392639 C202.07069519 115.77281311 202.06553894 116.91169983 202.06022644 118.08509827 C202.05088074 119.12271301 202.04153503 120.16032776 202.03190613 121.22938538 C202.44399165 124.57151185 203.3802309 126.43746542 205.38835144 129.12025452 C207.82645299 130.27500063 207.82645299 130.27500063 210.38835144 130.12025452 C212.92679153 128.30708303 213.38324169 127.13558376 214.38835144 124.12025452 C214.62357655 119.8324368 214.57353059 115.53883516 214.57585144 111.24525452 C214.59422058 109.46828186 214.59422058 109.46828186 214.61296082 107.65541077 C214.61489441 106.51201233 214.616828 105.36861389 214.61882019 104.19056702 C214.62498352 102.62459778 214.62498352 102.62459778 214.63127136 101.0269928 C214.37577076 97.96971625 213.83777428 95.82176805 212.38835144 93.12025452 C208.25508865 91.80112809 207.06599871 91.66848967 203.38835144 94.12025452 Z M204.63835144 147.37025452 C201.05459209 152.38751761 202.20402677 159.12089954 202.20085144 164.99525452 C202.18860535 166.17990295 202.17635925 167.36455139 202.16374207 168.58509827 C202.16180847 169.7284967 202.15987488 170.87189514 202.15788269 172.04994202 C202.1537738 173.09392151 202.14966492 174.137901 202.14543152 175.21351624 C202.40093212 178.27079278 202.9389286 180.41874098 204.38835144 183.12025452 C207.29840047 184.20248818 207.29840047 184.20248818 210.38835144 184.12025452 C213.43369263 182.50726618 213.43369263 182.50726618 214.06315613 180.364151 C214.79100335 175.3418959 214.61629615 170.2472004 214.63835144 165.18275452 C214.66928894 163.41254944 214.66928894 163.41254944 214.70085144 161.60658264 C214.70600769 160.46769592 214.71116394 159.3288092 214.71647644 158.15541077 C214.72582214 157.11779602 214.73516785 156.08018127 214.74479675 155.01112366 C214.33271123 151.66899719 213.39647198 149.80304361 211.38835144 147.12025452 C208.49014602 145.96097235 207.23502865 145.51548508 204.63835144 147.37025452 Z M125.38835144 162.12025452 C124.69354675 162.55595764 123.99874207 162.99166077 123.28288269 163.44056702 C115.30459542 168.91909073 110.4404132 176.21786496 107.70085144 185.43275452 C106.43896822 196.2849502 108.04645956 205.96039832 114.57585144 214.99525452 C121.33679763 222.93577004 129.76466366 227.22400095 140.07975769 228.43666077 C150.60983579 228.90100276 159.65525259 225.17352051 167.38835144 218.12025452 C174.70110701 211.21470575 177.85903628 202.7444565 178.41960144 192.78041077 C178.29909763 182.52252372 173.59083303 173.32273611 166.38835144 166.12025452 C154.45172772 157.76862349 138.48088592 153.67176533 125.38835144 162.12025452 Z M203.38835144 203.12025452 C201.63355083 208.38465635 202.1612616 213.98536122 202.13835144 219.49525452 C202.11772644 220.72759827 202.09710144 221.95994202 202.07585144 223.22962952 C202.07069519 224.41814514 202.06553894 225.60666077 202.06022644 226.83119202 C202.05088074 227.91706604 202.04153503 229.00294006 202.03190613 230.12171936 C202.43557331 233.51750044 203.37046769 235.38521563 205.38835144 238.12025452 C207.26792388 239.27791302 207.26792388 239.27791302 209.38835144 239.12025452 C212.46376626 237.36287462 213.24817142 236.54079458 214.38835144 233.12025452 C214.6503118 228.66613453 214.61980263 224.20624382 214.63835144 219.74525452 C214.65897644 218.51291077 214.67960144 217.28056702 214.70085144 216.01087952 C214.70858582 214.22810608 214.70858582 214.22810608 214.71647644 212.40931702 C214.72582214 211.32344299 214.73516785 210.23756897 214.74479675 209.11878967 C214.34112957 205.72300859 213.40623519 203.85529341 211.38835144 201.12025452 C207.82216498 199.27964215 206.13856136 200.46487942 203.38835144 203.12025452 Z "
        fill="currentcolor"
        transform="translate(47.61164855957031,117.87974548339844)"
      />
      <path
        d="M0 0 C3.91330321 1.84589774 6.09400778 3.63863117 7.9375 7.5 C9 11 9 11 8 15 C0.08 15 -7.84 15 -16 15 C-17.02494364 10.90022544 -16.85384943 9.41938057 -15.0703125 5.68359375 C-11.55036686 0.14674496 -6.07684653 -1.17655512 0 0 Z "
        fill="currentcolor"
        transform="translate(387,194)"
      />
    </svg>
  );
};
